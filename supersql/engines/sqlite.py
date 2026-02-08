import typing
import inspect
import asyncio
import logging
from functools import wraps
from typing import TYPE_CHECKING

from supersql.engines.connection import IConnection, IEngine
from supersql.utils.vendor_deps import validate_vendor_dependencies

# Validate dependencies at module level
validate_vendor_dependencies("sqlite")

import aiosqlite

logger = logging.getLogger('supersql.engines.sqlite')
from sqlite3.dbapi2 import Cursor


if(TYPE_CHECKING):
    from supersql.core.query import Query

CONNECTED_MESSAGE = "A connection already exists"
DISCONNECTED_MESSAGE = "No connection found to database"


def connected(f):
    if inspect.iscoroutinefunction(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            assert args[0]._connection is not None, DISCONNECTED_MESSAGE
            response = await f(*args, **kwargs)
            return response
    else:
        @wraps(f)
        def wrapper(*args, **kwargs):
            assert args[0]._connection is not None, DISCONNECTED_MESSAGE
            return f(*args, **kwargs)
    return wrapper


def disconnected(f):
    if inspect.iscoroutinefunction(f):
        @wraps(f)
        async def wrapper(*args, **kwargs): 
            assert args[0]._connection is None, CONNECTED_MESSAGE
            response = await f(*args, **kwargs)
            return response
    else:
        @wraps(f)
        def wrapper(*args, **kwargs):
            assert args[0]._connection is None, CONNECTED_MESSAGE
            return f(*args, **kwargs)
    return wrapper


class EngineConstructorArgs(typing.TypedDict):
    use_ssl: bool


class Engine(IEngine):
    def __init__(self, query, **kwargs: EngineConstructorArgs):
        self._query = query
        self._config = kwargs
        self._url = kwargs.get('database')
        
        if not self._url and query:
             self._url = query._database

        self.pool = None
    
    async def connect(self) -> None:
        assert self.pool is None, CONNECTED_MESSAGE
        logger.debug(f"Initializing SQLite pool for {self._url}")
        self.pool = Pool(self._url, **self._config)

    async def disconnect(self) -> None:
        assert self.pool is not None, DISCONNECTED_MESSAGE
        logger.debug("Closing SQLite pool")
        await self.pool.close()
        self.pool = None

    @property
    def parameter_placeholder(self) -> str:
        return "?"

    def connection(self) -> "Connection":
        if self.pool is None:
             self.pool = Pool(self._url, **self._config)
        return Connection(self.pool)
    

class Pool(object):
    def __init__(self, url: str, **kwargs: typing.Any):
        self._url = url
        self._config = kwargs
        self._min_size = kwargs.get('pool_min_size', 10)
        self._max_size = kwargs.get('pool_max_size', 10)
        self._timeout = kwargs.get('pool_timeout', 60)
        
        self._queue = asyncio.Queue(maxsize=self._max_size)
        self._current_size = 0
        self._lock = asyncio.Lock()
        logger.debug(f"SQLite Pool initialized with min={self._min_size}, max={self._max_size}")

    async def acquire(self) -> aiosqlite.Connection:
        try:
            connection = self._queue.get_nowait()
            logger.debug("Acquired SQLite connection from pool (idle)")
            return connection
        except asyncio.QueueEmpty:
            pass

        async with self._lock:
            if self._current_size < self._max_size:
                self._current_size += 1
                try:
                    invalid_args = {'database', 'host', 'port', 'user', 'password'}
                    connect_kwargs = {
                        k: v for k, v in self._config.items() 
                        if not k.startswith('pool_') and k not in invalid_args
                    }
                    connection = aiosqlite.connect(self._url, isolation_level=None, **connect_kwargs)
                    await connection.__aenter__()
                    logger.debug("Created new SQLite connection for pool")
                    return connection
                except Exception as e:
                    self._current_size -= 1
                    logger.error(f"Failed to create SQLite connection: {e}")
                    raise
        
        try:
            logger.debug("Waiting for SQLite connection from pool...")
            conn = await asyncio.wait_for(self._queue.get(), timeout=self._timeout)
            logger.debug("Acquired released SQLite connection")
            return conn
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for SQLite connection (timeout={self._timeout}s)")
            raise TimeoutError(f"Timed out waiting for connection from pool (timeout={self._timeout}s)")

    async def release(self, connection: aiosqlite.Connection) -> None:
        if connection:
            if self._queue.full():
                await connection.__aexit__(None, None, None)
                async with self._lock:
                    self._current_size -= 1
                logger.warning("Closed overflow SQLite connection")
            else:
                self._queue.put_nowait(connection)
                logger.debug("Released SQLite connection back to pool")

    async def close(self) -> None:
        count = 0
        while not self._queue.empty():
            try:
                conn = self._queue.get_nowait()
                await conn.__aexit__(None, None, None)
                count += 1
            except Exception:
                pass
        self._current_size = 0
        logger.debug(f"Closed {count} SQLite connections in pool")


class Connection(IConnection):
    def __init__(self, pool: Pool):
        self._pool = pool
        self._connection: typing.Union[None, aiosqlite.Connection] = None

    @disconnected
    async def begin(self) -> None:
        self._connection = await self._pool.acquire()

    @connected
    async def done(self) -> None:
        await self._pool.release(self._connection)
        self._connection = None
    
    @connected
    async def execute(self, query: 'Query') -> typing.Any:
        async with self._connection.execute(query.print()) as cursor:
            results = await cursor.fetchall()
            return results

    @connected
    async def fetchall(self, query: 'Query') -> typing.List[typing.Mapping]:
        async with self._connection.execute(query.print()) as cursor:
            self._connection.row_factory = aiosqlite.Row
            results = await cursor.fetchall()
            return results

    @connected
    async def fetchmany(self, limit: int) -> typing.Any:
        pass

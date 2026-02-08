import typing
import inspect
import logging
from functools import wraps
from typing import TYPE_CHECKING

from supersql.engines.connection import IConnection, IEngine
from supersql.utils.vendor_deps import validate_vendor_dependencies

# Validate dependencies at module level
validate_vendor_dependencies("mysql")

# Import MySQL dependencies after validation
import aiomysql

logger = logging.getLogger('supersql.engines.mysql')

if TYPE_CHECKING:
    from supersql.core.query import Query

CONNECTED_MESSAGE = "A connection already exists"
DISCONNECTED_MESSAGE = "No connection found to database"

USER, PASSWORD, HOST, PORT, DATABASE = 'user', 'password', 'host', 'port', 'database'


def connectable(f):
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


def disconnectable(f):
    if inspect.iscoroutinefunction(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            assert args[0]._connection, DISCONNECTED_MESSAGE
            response = await f(*args, **kwargs)
            return response
    else:
        @wraps(f)
        def wrapper(*args, **kwargs):
            assert args[0]._connection, DISCONNECTED_MESSAGE
            return f(*args, **kwargs)
    return wrapper


class EngineConstructorArgs(typing.TypedDict):
    user: str
    password: str
    port: int
    database: str
    host: str
    use_ssl: bool
    pool_min_size: int
    pool_max_size: int
    pool_timeout: int
    pool_recycle: int


class Engine(IEngine):
    def __init__(self, query, **kwargs: EngineConstructorArgs):
        self._query = query
        self._config = kwargs
        self.pool = None

    async def connect(self) -> None:
        assert self.pool is None, CONNECTED_MESSAGE
        logger.debug("Creating MySQL connection pool")
        
        # Extract pool arguments
        pool_min_size = self._config.get('pool_min_size', 10)
        pool_max_size = self._config.get('pool_max_size', 10)
        pool_timeout = self._config.get('pool_timeout', 60)
        pool_recycle = self._config.get('pool_recycle', -1)
        
        # Prepare connection arguments (exclude pool args)
        connect_kwargs = {k: v for k, v in self._config.items() if not k.startswith('pool_')}
        
        # aiomysql uses minsize, maxsize, pool_recycle, connect_timeout
        pool_kwargs = {
            'minsize': pool_min_size,
            'maxsize': pool_max_size,
            'connect_timeout': pool_timeout,
        }
        
        if pool_recycle > 0:
            pool_kwargs['pool_recycle'] = pool_recycle

        try:
            self.pool = await aiomysql.create_pool(**connect_kwargs, **pool_kwargs)
            logger.debug("MySQL connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create MySQL connection pool: {e}")
            raise

    async def disconnect(self) -> None:
        assert self.pool is not None, DISCONNECTED_MESSAGE
        logger.debug("Closing MySQL connection pool")
        try:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
            logger.debug("MySQL connection pool closed")
        except Exception as e:
            logger.error(f"Failed to close MySQL connection pool: {e}")
            raise
    
    @property
    def parameter_placeholder(self) -> str:
        return "%s"

    def connection(self) -> "Connection":
        return Connection(self.pool)


class Connection(IConnection):
    def __init__(self, pool):
        self._pool = pool
        self._connection = None

    @connectable
    async def begin(self) -> None:
        self._connection = await self._pool.acquire()

    @disconnectable
    async def done(self) -> None:
        await self._pool.release(self._connection)
        self._connection = None

    @disconnectable
    async def execute(self, query: 'Query') -> typing.Any:
        async with self._connection.cursor() as cursor:
            await cursor.execute(query.print(), query.args)
            return cursor.rowcount

    @disconnectable
    async def executemany(self, queries: typing.List['Query']) -> typing.Any:
        async with self._connection.cursor() as cursor:
            for query in queries:
                await cursor.execute(query.print(), query.args)
            return cursor.rowcount

    @disconnectable
    async def fetchall(self, query: "Query") -> typing.List[typing.Mapping]:
        async with self._connection.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query.print(), query.args)
            results = await cursor.fetchall()
            return results

    @disconnectable
    async def fetchmany(self, limit: int) -> typing.Any:
        # Implementation would depend on how the query is stored
        pass

    @disconnectable
    async def release(self) -> None:
        if self._connection:
            await self._pool.release(self._connection)
            self._connection = None

    @disconnectable
    async def rowcount(self, query: 'Query') -> int:
        async with self._connection.cursor() as cursor:
            await cursor.execute(query.print(), query.args)
            return cursor.rowcount

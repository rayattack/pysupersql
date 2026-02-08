import typing
import inspect
import logging
from functools import wraps
from typing import TYPE_CHECKING

from supersql.engines.connection import IConnection, IEngine
from supersql.utils.vendor_deps import validate_vendor_dependencies

# Validate dependencies at module level
validate_vendor_dependencies("postgres")

import asyncpg

logger = logging.getLogger('supersql.engines.postgres')


if(TYPE_CHECKING):
    from supersql.core.query import Query

CONNECTED_MESSAGE = "A connection already exists"
DISCONNECTED_MESSAGE = "Not connection found to database"

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
        logger.debug("Creating PostgreSQL connection pool")
        
        pool_min_size = self._config.get('pool_min_size', 10)
        pool_max_size = self._config.get('pool_max_size', 10)
        pool_timeout = self._config.get('pool_timeout', 60)
        pool_recycle = self._config.get('pool_recycle', -1)
        
        connect_kwargs = {k: v for k, v in self._config.items() if not k.startswith('pool_')}
        
        pool_kwargs = {
            'min_size': pool_min_size,
            'max_size': pool_max_size,
            'timeout': pool_timeout,
        }
        
        if pool_recycle > 0:
            pool_kwargs['max_inactive_connection_lifetime'] = pool_recycle

        try:
            self.pool = await asyncpg.create_pool(**connect_kwargs, **pool_kwargs)
            logger.debug("PostgreSQL connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL connection pool: {e}")
            raise

    async def disconnect(self) -> None:
        assert self.pool is not None, DISCONNECTED_MESSAGE
        logger.debug("Closing PostgreSQL connection pool")
        try:
            await self.pool.close()
            self.pool = None
            logger.debug("PostgreSQL connection pool closed")
        except Exception as e:
            logger.error(f"Failed to close PostgreSQL connection pool: {e}")
            raise

    @property
    def parameter_placeholder(self) -> str:
        return "$%d"

    def connection(self) -> "Connection":
        return Connection(self.pool)


class Connection(IConnection):
    def __init__(self, pool):
        self._pool = pool
        self._connection = None

    @disconnectable
    async def begin(self):
        self._connection = await self._pool.acquire()
        return self._connection

    @connectable
    async def done(self):
        await self._pool.release(self._connection)
        self._connection = None

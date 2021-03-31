import typing
import inspect
from functools import wraps
from typing import TYPE_CHECKING

import asyncpg

from supersql.engines.connection import IConnection, IEngine


if(TYPE_CHECKING):
    from supersql.core.query import Query

CONNECTED_MESSAGE = "A connection already exists"
DISCONNECTED_MESSAGE = "Not connection found to database"

USER, PASSWORD, HOST, PORT, DATABASE = 'user', 'password', 'host', 'port', 'database'


# Candidate for refactoring as much of connected and disconnected if Liskov not cared for
def connectable(f):
    if inspect.iscoroutinefunction(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            lettab = args[0]
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


class Engine(IEngine):
    def __init__(self, query, **kwargs: EngineConstructorArgs):
        self._query = query
        self._config = kwargs
        self.pool = None

    async def connect(self) -> None:
        assert self.pool is None, CONNECTED_MESSAGE
        self.pool = await asyncpg.create_pool(**self._config)

    async def disconnect(self) -> None:
        assert self.pool is not None, DISCONNECTED_MESSAGE
        await self.pool.close()
        self.pool = None

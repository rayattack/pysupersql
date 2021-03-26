import typing
import inspect
from functools import wraps
from typing import TYPE_CHECKING

import aiosqlite
from sqlite3.dbapi2 import Cursor

from supersql.engines.connection import IConnection, IEngine


if(TYPE_CHECKING):
    from supersql.core.query import Query

CONNECTED_MESSAGE = "A connection already exists"
DISCONNECTED_MESSAGE = "No connection found to database"


# Candidate for refactoring as much of connected and disconnected if Liskov not cared for
def connected(f):
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


def disconnected(f):
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
    use_ssl: bool


class Engine(IEngine):
    def __init__(self, url: str, **kwargs: EngineConstructorArgs):
        self._url = url
        self._config = kwargs
    
    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    def connection(self) -> "Connection":
        return Connection(self._url)
    

class Pool(object):
    def __init__(self, url: str, **kwargs: typing.Any):
        self._url = url
        self._config = kwargs

    async def connect(self) -> aiosqlite.Connection:
        connection = aiosqlite.connect(self._url, isolation_level=None, **self._config)
        await connection.__aenter__()
        return connection
    
    async def disconnect(self, connection: aiosqlite.Connection) -> None:
        exc_type, exc_val, exc_tb = None, None, None # Explicit for readability sake
        await connection.__aexit__(exc_type, exc_val, exc_tb)


class Connection(IConnection):
    def __init__(self, pool: Pool):
        self._pool = pool
        self._connection = typing.Union[None, aiosqlite.Connection]

    @disconnected
    async def begin(self) -> None:
        self._connection = await self._pool.connect()

    @connected
    async def done(self) -> None:
        await self._pool.disconnect()
        self._connection = None
    
    @connected
    async def execute(self, query: 'Query') -> typing.Any:
        with await self._connection.execute(query.print()) as cursor:
            results = await cursor.fetchall()
            return results

    @connected
    async def fetchall(self, query: 'Query') -> typing.List[typing.Mapping]:
        pass

    @connected
    async def fetchmany(self, limit: int) -> typing.Any:
        pass

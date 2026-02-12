import typing
import inspect
from functools import wraps
from typing import TYPE_CHECKING

from supersql.engines.connection import IConnection, IEngine
from supersql.utils.vendor_deps import validate_vendor_dependencies

# Validate dependencies at module level
validate_vendor_dependencies("mssql")

# Import SQL Server dependencies after validation
import aioodbc
# import pyodbc # Unused

if TYPE_CHECKING:
    from supersql.core.query import Query

CONNECTED_MESSAGE = "A connection already exists"
DISCONNECTED_MESSAGE = "No connection found to database"

USER, PASSWORD, HOST, PORT, DATABASE = 'user', 'password', 'host', 'port', 'database'


# Candidate for refactoring as much of connected and disconnected if Liskov not cared for
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
    driver: str
    use_ssl: bool


def _build_connection_string(config: EngineConstructorArgs) -> str:
    """Build SQL Server connection string from config."""
    driver = config.get('driver', 'ODBC Driver 17 for SQL Server')
    host = config['host']
    port = config.get('port', 1433)
    database = config['database']
    user = config['user']
    password = config['password']
    
    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={host},{port};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
    )
    
    if config.get('use_ssl', True):
        conn_str += "Encrypt=yes;TrustServerCertificate=no;"
    
    return conn_str


class Engine(IEngine):
    def __init__(self, query, **kwargs: EngineConstructorArgs):
        self._query = query
        self._config = kwargs
        self.pool = None

    async def connect(self) -> None:
        assert self.pool is None, CONNECTED_MESSAGE
        conn_str = _build_connection_string(self._config)
        self.pool = await aioodbc.create_pool(dsn=conn_str)

    async def disconnect(self) -> None:
        assert self.pool is not None, DISCONNECTED_MESSAGE
        self.pool.close()
        await self.pool.wait_closed()
        self.pool = None

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
        async with self._connection.cursor() as cursor:
            await cursor.execute(query.print(), query.args)
            columns = [column[0] for column in cursor.description]
            results = []
            async for row in cursor:
                results.append(dict(zip(columns, row)))
            return results

    @disconnectable
    async def fetchmany(self, limit: int) -> typing.Any:
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

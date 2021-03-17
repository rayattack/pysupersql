from asyncio import Lock
from importlib import import_module
from supersql.engines.sqlite import Engine
from types import ModuleType, TracebackType
from typing import List, Type
from typing import TYPE_CHECKING

from supersql.core.results import Results
from supersql.engines.connection import IConnection, IEngine

if TYPE_CHECKING:
    from supersql.core.query import Query

BASE = "supersql.engines."

ENGINES = {
    "postgres": f"{BASE}postgres",
    "mysql": f"{BASE}mysql"
}


class UnknownDriverException(Exception):...


class Database(object):
    """Represents a database and its properties

    Supersql Database Objects are proxies to the actual database
    and serve primarily to access and configure database
    properties programatically.

    ..properties:

    name {str}: Name of the database
    """

    def __init__(self, query: 'Query'):
        """
        Added here just before going to bed on 1st Feb 2021, might remove
        as this is not yet ratified. Query might be circular import?

        Do we want to keep everything centered around query objects?
        Might be a simple API but is the best design for the code?
        If everything is kept around query then
        q = Query()
        d = Database(q)
        """
        MODULE = self.runtime_module_resolver(query._vendor)

        self.Connection: IConnection = getattr(MODULE, 'Connection')
        self.Engine: IEngine = getattr(MODULE, 'Engine')

        self._engine: Engine = Engine(query)
        self.connected: bool = False
    
    async def __aenter__(self) -> 'Database':
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type: Type[BaseException] = None, exc_value: BaseException = None, tracebak: TracebackType = None) -> None:
        await self.disconnect()
    
    async def connect(self) -> None:
        assert not self.connected, "Connected already..."
        await self._engine.connect()
        self.connected = True
    
    async def disconnect(self) -> None:
        assert self.connected, "No existing connections found..."
        await self._engine.disconnect()
        self.connected = False
    
    async def execute(self, query: Query) -> Results:
        async with self.connection() as connection:
            pass
    
    def connection(self) -> "Connection":...

    @classmethod
    def runtime_module_resolver(module: str) -> ModuleType:
        try:
            return import_module(f'supersql.engines.{module}')
        except ImportError as exc:
            if exc.name != module:
                raise exc from None
            raise UnknownDriverException(f'Could not resolve {module} into a DB driver...')

    def tables(self):
        """
        Returns a list of all the tables in the database.

        Each table in the tables collection corresponds to a supersql.core.table.Table
        instance object.

        Tables to be returned from the database are lazily loaded, that means
        the real table collection will be inspected upon access.
        """
        pass


class Connection(object):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

        self._connectionlock = Lock()
        self._connection = self._engine.connection()
        self._counter = 0

        self._transactionlock = Lock()
        self._querylock = Lock()
    
    async def __aenter__(self) -> "Connection":
        async with self._connectionlock:
            self._counter += 1
            if self._counter == 1:
                await self._connection.begin()
        return self
    
    async def __aexit__(self, exc_type: Type[BaseException] = None, exc_val: BaseException = None, traceback: TracebackType = None):
        async with self._connectionlock:
            self._counter -= 1
            if self._counter == 0:
                await self._connection.done()

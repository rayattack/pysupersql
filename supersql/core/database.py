from asyncio import Lock
from importlib import import_module
from sys import version_info
from types import ModuleType, TracebackType
from typing import List, Type
from typing import TYPE_CHECKING

from supersql.core.results import Results
from supersql.engines.postgres import Engine
from supersql.engines.connection import IConnection, IEngine


if(TYPE_CHECKING):
    from supersql.core.query import Query


# The base of the path to tack on dynamic importing of engine module from
BASE = "supersql.engines."
CTX = "connection_context"


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

    def __init__(self, query: 'Query', **kwargs):
        """
        Added here just before going to bed on 1st Feb 2021, might remove
        as this is not yet ratified. Query might be circular import?

        Do we want to keep everything centered around query objects?
        Might be a simple API but is the best design for the code?
        If everything is kept around query then
        q = Query()
        d = Database(q)
        """
        MODULE = self.runtime_module_resolver(query._engine)

        self.Engine: IEngine = getattr(MODULE, 'Engine')

        self._engine: Engine = Engine(query, **kwargs)
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

    async def executes(self, query: 'Query', consequence=None, limit=None, transactions=False) -> Results:
        async with self._engine.pool.acquire() as connection:
            if query._consequence == 'DQL': method = connection.fetch
            elif query._consequence == 'DML': method = connection.fetchval
            else: method = connection.execute

            if query._unsafe: return await method(query.print())
            else: return await method(query.print(), *query.args)

    async def raw(self, sql: str) -> Results:
        async with self._engine.pool.acquire() as connection:
            return await connection.execute(sql)

    @staticmethod
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

    def table(self, tablename):
        """
        Returns a reflection of the table schema in the database into
        a python object that supports supersql overloaded comparators and ops
        logic for querying.
        """
        pass

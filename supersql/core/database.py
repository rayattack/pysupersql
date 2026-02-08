from asyncio import Lock, run as asyncio_run
from importlib import import_module
from sys import version_info
from types import ModuleType, TracebackType
from typing import List, Type, Optional, Any, Dict
from typing import TYPE_CHECKING
import logging

from supersql.core.results import Results
from supersql.engines.postgres import Engine
from supersql.engines.connection import IConnection, IEngine
from supersql.errors import VendorDependencyError, UnsupportedVendorError
from supersql.utils.vendor_deps import (
    validate_vendor_dependencies,
    is_vendor_supported,
    get_installation_command,
    VENDOR_DEPENDENCIES
)

logger = logging.getLogger('supersql.core.database')


if(TYPE_CHECKING):
    from supersql.core.query import Query
    from supersql.core.table import Table


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

    def __init__(self, query: 'Query', **kwargs: Any):
        """
        Added here just before going to bed on 1st Feb 2021, might remove
        as this is not yet ratified. Query might be circular import?

        Do we want to keep everything centered around query objects?
        Might be a simple API but is the best design for the code?
        If everything is kept around query then
        q = Query()
        d = Database(q)
        """
        try:
            self._engine = self._get_engine_instance(query, **kwargs)
            logger.debug(f"Initialized Database with engine for: {query._engine}")
        except Exception:
            logger.error(f"Failed to initialize Database engine for: {query._engine}")
            raise
            
        self.connected: bool = False

    def _get_engine_instance(self, query: 'Query', **kwargs: Any) -> IEngine:
        """
        Resolves and instantiates the appropriate database engine.
        
        Args:
            query: The Query object
            **kwargs: Configuration arguments
            
        Returns:
            An instantiated Engine object
        """
        try:
            module = self.runtime_module_resolver(query._engine)
            engine_class = getattr(module, 'Engine')
            return engine_class(query, **kwargs)
        except Exception as e:
            logger.error(f"Error resolving engine instance: {e}")
            raise e

    async def __aenter__(self) -> 'Database':
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Optional[Type[BaseException]] = None, exc_value: Optional[BaseException] = None, tracebak: Optional[TracebackType] = None) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        assert not self.connected, "Connected already..."
        logger.info(f"Connecting to database: {self._engine.__class__.__name__}")
        try:
            await self._engine.connect()
            self.connected = True
            logger.info("Successfully connected to database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def disconnect(self) -> None:
        assert self.connected, "No existing connections found..."
        logger.info("Disconnecting from database")
        try:
            await self._engine.disconnect()
            self.connected = False
            logger.info("Successfully disconnected from database")
        except Exception as e:
            logger.error(f"Failed to disconnect from database: {e}")
            raise

    def connects(self) -> None:
        """
        Synchronous version of connect.
        
        Establishes a connection to the database synchronously.
        Use this when you need synchronous database access.
        """
        asyncio_run(self.connect())

    def disconnects(self) -> None:
        """
        Synchronous version of disconnect.
        
        Closes the database connection synchronously.
        """
        asyncio_run(self.disconnect())

    async def rollback(self) -> None:
        """
        Rollback the current transaction
        """
        if hasattr(self._engine, 'rollback'):
            await self._engine.rollback()
            
    def rollbacks(self) -> None:
        """
        Synchronous version of rollback
        """
        asyncio_run(self.rollback())

    async def execute(self, query: 'Query', consequence=None, limit=None, transactions=False) -> Results:
        # Ensure query is built
        sql = query.build()
        logger.debug(f"Executing query: {sql}")
        try:
            async with self._engine.pool.acquire() as connection:
                if query._consequence == 'DQL': method = connection.fetch
                elif query._consequence == 'DML': method = connection.fetchval
                else: method = connection.execute
    
                if query._unsafe: return await method(sql)
                else: return await method(sql, *query.args)
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def executes(self, query: 'Query', consequence=None, limit=None, transactions=False) -> Results:
        """
        Synchronous version of execute.
        
        Executes a query against the database synchronously.
        
        Args:
            query: The Query object to execute
            consequence: Optional consequence type override
            limit: Optional limit on results
            transactions: Whether to use transactions
        
        Returns:
            Results: A Results object containing query results
        """
        return asyncio_run(self.execute(query, consequence, limit, transactions))

    async def raw(self, sql: str) -> Results:
        async with self._engine.pool.acquire() as connection:
            return await connection.execute(sql)

    @staticmethod
    def runtime_module_resolver(module: str) -> ModuleType:
        # Check if vendor is supported
        if not is_vendor_supported(module):
            supported_vendors = list(VENDOR_DEPENDENCIES.keys())
            raise UnsupportedVendorError(module, supported_vendors)

        try:
            return import_module(f'supersql.engines.{module}')
        except VendorDependencyError:
            # Re-raise vendor dependency errors as-is
            raise
        except ImportError as exc:
            # Check if this is a missing vendor dependency
            if any(dep in str(exc) for dep in VENDOR_DEPENDENCIES.get(module, [])):
                install_cmd = get_installation_command(module)
                raise VendorDependencyError(
                    module,
                    VENDOR_DEPENDENCIES.get(module, []),
                    f"Missing dependencies for {module}. Install with: {install_cmd}"
                ) from exc

            # Other import errors
            if exc.name != module:
                raise exc from None
            raise UnknownDriverException(f'Could not resolve {module} into a DB driver...')

    async def tables(self) -> Dict[str, 'Table']:
        """
        Returns a list of all the tables in the database.

        Each table in the tables collection corresponds to a supersql.core.table.Table
        instance object.

        Tables to be returned from the database are lazily loaded, that means
        the real table collection will be inspected upon access.
        """
        from supersql.reflection.inspector import DatabaseInspector

        inspector = DatabaseInspector(self)
        return await inspector.get_all_tables()

    async def table(self, tablename: str) -> 'Table':
        """
        Returns a reflection of the table schema in the database into
        a python object that supports supersql overloaded comparators and ops
        logic for querying.

        Args:
            tablename: Name of the table to reflect

        Returns:
            Table: A supersql.core.table.Table instance with reflected schema
        """
        from supersql.reflection.inspector import DatabaseInspector

        inspector = DatabaseInspector(self)
        return await inspector.reflect_table(tablename)

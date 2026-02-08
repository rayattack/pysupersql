from asyncio import run as asyncio_run
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from threading import Event
from numbers import Number
import copy


import logging
from typing import Union, Optional

from supersql.errors import (
    ArgumentError,
    MissingArgumentError,
    MissingCommandError,
    DatabaseError,
    ProgrammingError
)

from .database import Database
from .table import Table
from .results import Results
from .state import QueryState
from .compiler import PostgresCompiler, MySQLCompiler, SQLiteCompiler

logger = logging.getLogger('supersql.core.query')

_loop = None


SUPPORTED_ENGINES = (
    "sqlite",
    "postgres",
    "postgresql",
    "oracle",
    "oracledb",
    "mariadb",
    "mysql",
    "mssql",
    "sqlserver",
    "athena",
    "presto"
)

_AND = " AND"
DELETE = "DELETE"
SELECT = "SELECT"
_FROM_ = " FROM "
INSERT_INTO_ = "INSERT INTO "
VALUES_ = "VALUES "
UPDATE_ = "UPDATE "
WHERE = "WHERE"

DDL = 'DDL'
DML = 'DML'
DQL = 'DQL'


class Query(object):
    """Query objects are the pipes through which ALL communication to
    the database is made.

    A query is the work horse for supersql as it is in SQL. Queries
    can be connected to the database or isolated and used for only
    generating engine specific SQL strings.
    """

    def __init__(
        self, 
        engine: str, 
        dsn: Optional[str] = None, 
        user: Optional[str] = None, 
        password: Optional[str] = None, 
        host: Optional[str] = None, 
        port: Optional[int] = None, 
        database: Optional[str] = None, 
        silent: bool = True, 
        unsafe: bool = False,
        pool_min_size: int = 10,
        pool_max_size: int = 10,
        pool_timeout: int = 60,
        pool_recycle: int = -1
    ):
        """Query constructor
        Sets up a query engine for use by saving initialization
        parameters internally for use in connecting to the backing
        database engine as required to execute queries.

        ..params:

        engine {str | required}:
            The database engine i.e. postgres, oracle,
            mysql, mssql etc.
        user {str | optional}:
            The user to connect as
        
        password {str | optional}:
            The password for the provided user
        
        host {str | optional}:
            Where is the server seated, what ip, port and what is the
            name of the database?
        
        silent {bool | optional}:
            Flag to specify if there should be syntax check i.e. should
            supersql check for an error in your prepared query before even
            sending it out to the database engine?
            Defaults to `True` i.e. do not check for errors
        
        pool_min_size {int | optional}:
            Minimum connections to keep in the pool.
            Defaults to 10
        
        pool_max_size {int | optional}:
            Maximum connections to keep in the pool.
            Defaults to 10
            
        pool_timeout {int | optional}:
            Timeout in seconds for acquiring a connection from the pool.
            Defaults to 60
            
        pool_recycle {int | optional}:
            Number of seconds after which a connection is automatically
            recycled. -1 means no recycling.
            Defaults to -1
        """
        # Handle connection string format: postgres://user:password@host:port/database
        self._pool_min_size = pool_min_size
        self._pool_max_size = pool_max_size
        self._pool_timeout = pool_timeout
        self._pool_recycle = pool_recycle

        if engine and '://' in str(engine):
            parsed = self._parse_connection_string(engine)
            self._engine = parsed['engine']
            self._dsn = engine
            self._user = user or parsed.get('user')
            self._password = password or parsed.get('password')
            self._host = host or parsed.get('host')
            self._port = port or parsed.get('port')
            self._database = database or parsed.get('database')
        else:
            if engine not in SUPPORTED_ENGINES:
                raise NotImplementedError(f"{engine} is not a supersql supported engine")
            self._engine = engine
            self._dsn = dsn
            self._user = user
            self._password = password
            self._host = host
            self._port = port
            self._database = database
        self._silent = silent
        self._state = QueryState()
        
        # Initialize Compiler based on engine
        if self._engine in ('postgres', 'postgresql'):
             self._compiler = PostgresCompiler()
        elif self._engine == 'mysql':
             self._compiler = MySQLCompiler()
        elif self._engine == 'sqlite':
             self._compiler = SQLiteCompiler()
        else:
             # Fallback or error? For now default to Postgres or raise
             # raise NotImplementedError(f"Compiler for {self._engine} not implemented")
             # Use Postgres as default just to not crash, but this is dangerous
             self._compiler = PostgresCompiler() 
              
        self._pristine = True
        self._disparity = 0  # how many tables is this query for?
        self._from = []
        self._callstack = []

        self._unsafe = unsafe

        self._args = []

        self._consequence = DQL  # we default to reads
        self._tablenames = set()
        self._orphans = set()
        self._alias = None

        # continuation primitives
        self._pause_cloning = False
        self._t_ = ''  # used to determine if to put a semi-colon and space before commands

        _params = {
            "host": self._host, 
            "port": self._port, 
            "user": self._user, 
            "password": self._password, 
            "database": self._database,
            "pool_min_size": pool_min_size,
            "pool_max_size": pool_max_size,
            "pool_timeout": pool_timeout,
            "pool_recycle": pool_recycle
        }
        self._db = Database(self, **_params)

    def _parse_connection_string(self, connection_string: str) -> dict:
        """
        Parse a connection string like postgres://user:password@host:port/database

        Args:
            connection_string: Connection string to parse

        Returns:
            Dictionary with parsed connection parameters
        """
        import re

        if connection_string.startswith('sqlite:'):
             # Handle sqlite specially as it may not strictly follow user:pass@host:port format
             # e.g supersql currently receives sqlite:///path/to/db (absolute) or sqlite://path/to/db (relative)
             # We just take everything after sqlite:// as the database path/url
             path_match = re.match(r'^sqlite://(.*)$', connection_string)
             if path_match:
                 return {
                     'engine': 'sqlite',
                     'database': path_match.group(1),
                     'host': None,
                     'port': None,
                     'user': None,
                     'password': None
                 }

        # Pattern to match: engine://user:password@host:port/database
        pattern = r'^(\w+)://(?:([^:]+)(?::([^@]+))?@)?([^:/]+)(?::(\d+))?/(.+)$'
        match = re.match(pattern, connection_string)

        if not match:
            raise ValueError(f"Invalid connection string format: {connection_string}")

        engine, user, password, host, port, database = match.groups()

        # Map postgresql to postgres for compatibility
        if engine == 'postgresql':
            engine = 'postgres'

        return {
            'engine': engine,
            'user': user,
            'password': password,
            'host': host,
            'port': int(port) if port else None,
            'database': database
        }



    def _clone(self) -> "Query":
        """
        # ! Why copy of Query object is returned
        # A copy of query is returned so internal query variables do not
        # leak out to other query objects.
        #
        # i.e. it is possible to declare a global query object with connection
        # configuration and reuse without fear of internal state corruption
        """
        new_query = type(self)(
            engine=self._engine,
            dsn=self._dsn,
            user=self._user,
            password=self._password,
            host=self._host,
            silent=self._silent,
            port=self._port,
            database=self._database,
            unsafe=self._unsafe,
            pool_min_size=self._pool_min_size,
            pool_max_size=self._pool_max_size,
            pool_timeout=self._pool_timeout,
            pool_recycle=self._pool_recycle
        )
        
        if not self._pause_cloning:
            new_query._state = copy.deepcopy(self._state)
            # Copy other internal state if needed
            new_query._tablenames = self._tablenames.copy()
            new_query._orphans = self._orphans.copy()
            new_query._callstack = self._callstack.copy()
            new_query._from = self._from.copy()
            new_query._args = self._args.copy()
            return new_query
            
        return self

    def _chain_state(self):
        """
        If the current state represents a complete statement,
        archive it into the chain and start a fresh state.
        """
        s = self._state
        # Check if state is modified/dirty
        is_dirty = (s.statement_type != 'SELECT') or (len(s.selects) > 0) or (len(s.from_sources) > 0)
        
        if is_dirty:
            old_state = self._state
            new_state = QueryState()
            new_state.chain = old_state.chain + [old_state]
            self._state = new_state

    def _conditionator(self, condition):
        if isinstance(condition, str):
            return f" {condition}"
        else:
            try:
                return f" {condition.print(self)}"
            except AttributeError:
                msg = "Where clause can only process strings or column comparison operations"
                raise ArgumentError(msg)
    
    @property
    def args(self):
        return self._args

    @property
    def database(self) -> Database:
        """
        Get the database for inspection or operation
        """
        return self._db

    def execute(self, *args, **kwargs) -> Results:
        """
        Flushes the SQL command to the server for execution (synchronous).

        This is a synchronous wrapper around the async `run()` method.
        Use this when you need synchronous database access.

        ..raises:
        {ConnectionError} On failed connection attempts to the database engine

        {StatementError} When the SQL Statement is malformed i.e. before being
            sent to the database engine and only if `silent = False`
        
        {CommandError} When the database server could not execute the command
            sent from preparation of your query. Wraps the message of the
            database server internally for easy debugging.
        
        Returns:
            Results: A Results object containing the query results
        """
        return asyncio_run(self.run(*args, **kwargs))

    def get_tablename(self, table: Union[str, Table, None]) -> str:
        """
        Irrespective of the type of naming convention used i.e.
        3 part "schema.table.columnname" or 4 part "db.schema.table.columnname"
        this method expects the second part from the right to always be 
        table name
        """
        if isinstance(table, Table):
            return Table.__tn__()
        elif isinstance(table, str):
            processed = table.split(".")
            parts = len(processed)
            return None if parts < 2 else processed[-2]
        else:
            column = table
            return column._imeta.__tn__()
    
    def print(self):
        """
        Prints the current SQL statement as it exists on the query object

        ..return {str}  String representation of the SQL command to be sent
            to the database server if `execute` method is called.
        """
        # If we have state, compile it
        return self._compiler.compile(self._state)
    
    async def run(self, *args, **kwargs) -> Results:
        async with self._db as db:
            results = await db.execute(self)
            return Results(results)

    async def sql(self, statement: str):
        async with self._db as db:
            results = await db.raw(statement)
            return results

    def was_called(self, command):
        return command in self._callstack

    def warn(self, command):
        if self._callstack[-1] == command:
            msg = f'Invalid Query Chaining: repeated {command} more than once'
            raise ProgrammingError(msg)
    
    def AND(self, condition):
        snippet = self._conditionator(condition).strip()
        self._state.wheres.append(snippet)
        return self

    def AS(self, alias):
        """
        If select was last called then use this as the alias for select
        """
        self._alias = alias
        return self

    def BEGIN(self):
        this = self._clone()
        this._t_ = '; '
        this._pause_cloning = True
        this._callstack.append('BEGIN')
        
        this._chain_state()
        this._state.statement_type = 'BEGIN'
        return this
    
    def COMMIT(self):
        self._pause_cloning = False
        self._callstack.append('COMMIT')
        
        self._chain_state()
        self._state.statement_type = 'COMMIT'
        self._t_ = ''  # reset here not necessary but hey...
        return self

    def DELETE(self, table):
        return self.DELETE_FROM(table)

    def DELETE_FROM(self, table):
        this = self._clone()
        this._callstack.append(DELETE)
        
        this._chain_state()
        this._state.statement_type = 'DELETE'
        
        if isinstance(table, str):
            tablename = table
        elif isinstance(table, Table):
            tablename = table.__tn__()
        else:
             raise ArgumentError(f"DELETE FROM expects a table name or Table object, got {type(table)}")
        
        this._state.from_sources.append(tablename)
        return this

    def FETCH(self, *args):
        return self

    def FROM(self, *args, **kwargs):
        """
        Adds sources to the FROM clause.
        """
        self._callstack.append(_FROM_)

        num_of_args = len(args)
        num_of_tables = len(self._tablenames)
        msg = f"tables:{num_of_tables}, args:{num_of_args}"

        if num_of_args != num_of_tables and num_of_tables > 0:
            raise MissingArgumentError(msg)

        froms_to_add = []
        for source in args:
            has_alias = None
            if isinstance(source, str):
                _a = None
                _q = source
            elif isinstance(source, Query):
                _a = source._alias
                # Nested Query: store the string for now to match legacy behavior
                _q = f"({source.print()})"
            elif isinstance(source, Table):
                _a = source._alias
                _q = source.__tn__()
            else:
                 raise ArgumentError(f"FROM expects string, Query, or Table, got {type(source)}")

            _from = f"{_q} AS {_a}" if _a and num_of_tables > 1 else f"{_q}"
            froms_to_add.append(_from)

        self._state.from_sources.extend(froms_to_add)
        
        # Legacy support
        self._from.extend(froms_to_add)
        return self

    def GROUP_BY(self, *args):
        """
        Add GROUP BY clause to the query.
        """
        self._callstack.append('GROUP_BY')
        
        cols = []
        for arg in args:
            if isinstance(arg, str):
                cols.append(arg)
            elif isinstance(arg, Table):
                cols.extend(arg.columns())
            else:
                # Column/Field object
                cols.append(arg._name)
        
        if cols:
            self._state.groups.extend(cols)
        return self

    def INSERT_INTO(self, table: str, *args):
        this = self._clone()
        this._consequence = DML
        this._insert_args = len(args) # only available when insert into is the sql command
        this._callstack.append(INSERT_INTO_)
        this._pause_cloning = True
        
        this._chain_state()
        this._state.statement_type = 'INSERT'

        if isinstance(table, Table):
            t = table.__tn__()
        else:
            t = table
            
        this._state.insert_table = t
        
        # Flatten args
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            cols = list(args[0])
        else:
            cols = list(args)
            
        this._state.insert_columns = cols
        return this

    def JOIN(self, table, on=None, join_type='INNER'):
        """
        Add a JOIN clause to the query.

        Args:
            table: Table name (str) or Table object to join
            on: Join condition (str or column comparison)
            join_type: Type of join - 'INNER', 'LEFT', 'RIGHT', 'FULL', 'CROSS'
        
        Returns:
            Query: self for method chaining
        """
        self._callstack.append('JOIN')
        
        # Get table name
        if isinstance(table, Table):
            tablename = table.__tn__()
            alias = table._alias
        elif isinstance(table, str):
            tablename = table
            alias = None
        else:
            raise ArgumentError(f"JOIN expects a table name or Table object, got {type(table)}")
        
        # Build JOIN clause
        join_sql = f"{join_type} JOIN {tablename}"
        if alias:
            join_sql += f" AS {alias}"
        
        # Add ON condition if provided
        if on is not None:
            if isinstance(on, str):
                join_sql += f" ON {on}"
            else:
                # Column comparison object
                join_sql += f" ON {on.print(self)}"
        

        
        
        self._state.joins.append(join_sql)
        return self
    
    def LEFT_JOIN(self, table, on=None):
        """Convenience method for LEFT JOIN."""
        return self.JOIN(table, on, join_type='LEFT')
    
    def RIGHT_JOIN(self, table, on=None):
        """Convenience method for RIGHT JOIN."""
        return self.JOIN(table, on, join_type='RIGHT')
    
    def FULL_JOIN(self, table, on=None):
        """Convenience method for FULL OUTER JOIN."""
        return self.JOIN(table, on, join_type='FULL OUTER')
    
    def CROSS_JOIN(self, table):
        """Convenience method for CROSS JOIN (no ON clause)."""
        return self.JOIN(table, on=None, join_type='CROSS')

    def LIMIT(self, count, offset=None):
        """
        Add LIMIT clause to the query.

        Args:
            count: Maximum number of rows to return
            offset: Optional number of rows to skip
        
        Returns:
            Query: self for method chaining
        """
        self._callstack.append('LIMIT')
        if offset is not None: self._sql.append(f" LIMIT {count} OFFSET {offset}")
        else: self._sql.append(f" LIMIT {count}")
        return self

    def ORDER_BY(self, *args):
        """
        Add ORDER BY clause to the query.

        Use negative prefix (-column) for descending order.
        
        Args:
            *args: Column names, column objects, or negated columns for DESC
        
        Returns:
            Query: self for method chaining
        
        Example:
            query.ORDER_BY('name')  # ORDER BY name ASC
            query.ORDER_BY('-age')  # ORDER BY age DESC (string with - prefix)
        """
        self._callstack.append('ORDER_BY')
        
        order_parts = []
        for arg in args:
            if isinstance(arg, str):
                if arg.startswith('-'):
                    order_parts.append(f"{arg[1:]} DESC")
                else:
                    order_parts.append(f"{arg} ASC")
            elif isinstance(arg, Table):
                # Order by all columns in table
                for col in arg.columns():
                    order_parts.append(f"{col} ASC")
            else:
                # Column/Field object
                order_parts.append(f"{arg._name} ASC")
        
        if order_parts:
            self._state.orders.extend(order_parts)
        return self

    def RETURNING(self, *args):
        self._callstack.append('RETURNING')
        parsed = []

        for arg in args:
            if isinstance(arg, Table):
                col = arg.__tn__()
            elif isinstance(arg, str):
                col = arg
            else: #Field Object
                col = arg._name
            parsed.append(col)

        parsed = parsed or ['*']

        parsed = parsed or ['*']
        self._state.returning = parsed
        return self

    def SELECT(self, *args):
        this = self._clone()
        this._consequence = DQL
        this._callstack.append(SELECT)
        
        if this._state.statement_type in ('UPDATE', 'DELETE', 'BEGIN', 'COMMIT'):
            this._chain_state()
            this._state.statement_type = 'SELECT'
        elif this._state.statement_type != 'INSERT':
            this._state.statement_type = 'SELECT'

        num_of_args = len(args)
        cols = []
        
        if num_of_args == 0:
            separator = "*" 
            cols.append("*")
        elif num_of_args == 1:
            arg = args[0]
            if isinstance(arg, str):
                _table = this.get_tablename(arg)
                this._tablenames.add(
                    _table
                ) if _table else this._orphans.add(arg)
                cols.append(arg)
            elif isinstance(arg, Table):
                this._tablenames.add(arg.__tn__())
                cols.append("*") 
            else:
                this._tablenames.add(arg._meta.__tn__())
                cols.append(arg._name)
        else:
            unique_tablenames = set([this.get_tablename(table) for table in args])
            is_heterogeneous = len(unique_tablenames) > 1

            for member in args:
                if isinstance(member, str):
                    _table = this.get_tablename(member)
                    this._tablenames.add(_table) if _table else None
                    cols.append(member)
                elif isinstance(member, Table):
                    # activate alias on tables if is_heterogeneous
                    if is_heterogeneous:
                        member.AS(member._alias if member._alias else member.__tn__())

                    this._tablenames.add(member.__tn__())
                    cols.extend(member.columns())
                else:
                    # Column object
                    alias = member._imeta._alias
                    tablename = member._imeta.__tn__()
                    member._imeta.AS(alias if alias else tablename)

                    this._tablenames.add(tablename)
                    if is_heterogeneous:
                        cols.append(f"{member._imeta._alias}.{member._name}")
                    else:
                        cols.append(f"{member._name}")

        this._state.selects = cols
        return this

    def SET(self, *args):
        self._callstack.append('SET')
        updates = [ax if isinstance(ax, (str, Number)) else ax.print(self) for ax in args]
        self._state.updates.extend(updates)
        return self

    def UNION(self, *args):
        """UNION is not yet implemented."""
        raise NotImplementedError(
            "UNION is not yet implemented in supersql. "
            "Consider using raw SQL via query.sql() for complex unions."
        )

    def UPDATE(self, table):
        this = self._clone()
        this._consequence = DML
        this._chain_state()
        this._state.statement_type = 'UPDATE'
        this._callstack.append(UPDATE_)
        
        tn = table if isinstance(table, str) else table.__tn__()
        this._state.update_table = tn
        return this

    def UPSERT(self, *args):
        """UPSERT is not yet implemented (vendor-specific syntax)."""
        raise NotImplementedError(
            "UPSERT is not yet implemented in supersql. "
            "Syntax varies by database vendor (INSERT ... ON CONFLICT for PostgreSQL, "
            "INSERT ... ON DUPLICATE KEY for MySQL). Use raw SQL via query.sql()."
        )

    def VALUES(self, *args):
        self._callstack.append(VALUES_)
        vals = []

        def xfy(val):
            """Make vale sql friendly i.e. convert dates, booleans etc to sql types"""
            if isinstance(val, str): val = val.replace("'", "''") 
            elif isinstance(val, bool): val = 'true' if val else 'false'

            return f"{val}"

        for values in args:
            _wparens = ', '.join(f"'{xfy(value)}'" if isinstance(value, (str, bool)) else f"{value}" for value in values)
            sql = f"({_wparens})"
            vals.append(sql)

        self._state.values.extend(vals)
        return self

    def WHERE(self, condition):
        """
        Check if _from was called and populate wheres.
        """
        if UPDATE_ in self._callstack: pass
        elif _FROM_ not in self._callstack:
            if DELETE not in self._callstack:
                tablenames = self._tablenames
                self = self.FROM(*tablenames)

        self._callstack.append(WHERE)
        
        # Use conditionator to get the string representation
        snippet = self._conditionator(condition).strip() # Strip leading space
        self._state.wheres.append(snippet)
        
        return self

    def WITHOUT(self, *args):
        """WITHOUT is not yet implemented."""
        raise NotImplementedError(
            "WITHOUT is not yet implemented in supersql."
        )

    def WITH(self, alias, query):
        """
        Add a Common Table Expression (CTE) to the query.
        
        Args:
            alias: The name of the CTE.
            query: A Query object or SQL string string.
        """
        this = self._clone()
        this._state.ctes.append((alias, query))
        return this
             
        # Add to state
        this._state.ctes.append((val_alias, query))
        return this


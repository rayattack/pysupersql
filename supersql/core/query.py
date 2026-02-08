from asyncio import run as asyncio_run
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from threading import Event
from numbers import Number
import copy


import logging
from typing import Union, Optional, Any

from supersql.errors import (
    ArgumentError,
    MissingArgumentError,
    MissingCommandError,
    DatabaseError,
    ProgrammingError,
    ValidationError
)

from .database import Database
from .table import Table
from .results import Results
from .state import QueryState
from .compiler import PostgresCompiler, MySQLCompiler, SQLiteCompiler
from .window import (
    WindowSpec,
    ROW_NUMBER as _ROW_NUMBER,
    RANK as _RANK,
    DENSE_RANK as _DENSE_RANK,
    NTILE as _NTILE,
    PERCENT_RANK as _PERCENT_RANK,
    CUME_DIST as _CUME_DIST,
    LAG as _LAG,
    LEAD as _LEAD,
    FIRST_VALUE as _FIRST_VALUE,
    LAST_VALUE as _LAST_VALUE,
    NTH_VALUE as _NTH_VALUE,
    WindowSum,
    WindowAvg,
    WindowCount,
    WindowMin,
    WindowMax
)

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
        pool_recycle: int = -1,
        schema: Optional[Any] = None
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
        self._schema = schema

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
        
        if self._engine in ('postgres', 'postgresql'):
             self._compiler = PostgresCompiler()
        elif self._engine == 'mysql':
             self._compiler = MySQLCompiler()
        elif self._engine == 'sqlite':
             self._compiler = SQLiteCompiler()
        else:
             self._compiler = PostgresCompiler() 
              
        self._pristine = True
        self._disparity = 0
        self._from = []
        self._callstack = []

        self._unsafe = unsafe

        self._args = []

        self._consequence = DQL
        self._tablenames = set()
        self._orphans = set()
        self._alias = None

        self._pause_cloning = False
        self._t_ = ''

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

        pattern = r'^(\w+)://(?:([^:]+)(?::([^@]+))?@)?([^:/]+)(?::(\d+))?/(.+)$'
        match = re.match(pattern, connection_string)

        if not match:
            raise ValueError(f"Invalid connection string format: {connection_string}")

        engine, user, password, host, port, database = match.groups()

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
        # Allow Condition objects to pass through to compiler
        return condition

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

    def get_tablename(self, table: Union[str, Table, None]) -> Optional[str]:
        if hasattr(table, '__tn__'):
            return table.__tn__()
        elif isinstance(table, str):
            # Extract table name from string "table.column" or "schema.table.column"
            # Logic: last part is column, second to last is table.
            processed = table.split(".")
            parts = len(processed)
            if parts >= 2:
                # e.g. "users.id" -> "users"
                return processed[-2]
            return None
        else:
            # Field object
            if hasattr(table, 'table') and table.table:
                return table.table.__tn__()
            return None
    
    def build(self) -> str:
        """
        Compiles the current state to a SQL string and updates self._args w/ parameters.
        Returns the SQL string.
        """
        if not self._state.statement_type:
            return ""
            
        sql, params = self._compiler.compile(self._state)
        # Update bound parameters
        self._args = params
        return sql

    def print(self):
        """
        Prints the current SQL statement as it exists on the query object
        
        ..return {str}  String representation of the SQL command
        """
        sql = self.build()
        print(sql)
        if self._args:
            print(f"Parameters: {self._args}")
        return sql
    
    async def run(self, *args, **kwargs) -> Results:
        # Build SQL and parameters before execution
        self.build()
        async with self._db as db:
            results = await db.execute(self)
            return Results(results)

    async def sql(self, statement: str = None):
        """
        Execute raw SQL.
        """
        if statement:
             async with self._db as db:
                results = await db.raw(statement)
                return results
        return None

    def was_called(self, command):
        return command in self._callstack

    def warn(self, command):
        if self._callstack[-1] == command:
            msg = f'Invalid Query Chaining: repeated {command} more than once'
            raise ProgrammingError(msg)
    
    def AND(self, condition):
        # Append condition directly
        self._state.wheres.append(condition)
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
        
        if isinstance(table, str): tablename = f'"{table}"'
        elif isinstance(table, Table): tablename = table.__tn__()
        else:
             raise ArgumentError(f"DELETE FROM expects a table name or Table object, got {type(table)}")
        
        this._state.from_sources.append(tablename)
        return this

    def FETCH(self, *args):
        return self

    def FROM(self, *args, **kwargs):
        if not args:
            raise ArgumentError("FROM requires at least one table argument")

        self._callstack.append(_FROM_)

        froms_to_add = []
        for source in args:
            _from = ""
            if isinstance(source, str):
                # Quote string table names in FROM
                _from = f'"{source}"'
            elif isinstance(source, Query):
                _a = source._alias
                # Quote alias if present
                alias_part = f' AS "{_a}"' if _a else ""
                _from = f"({source.print()}){alias_part}"
            elif hasattr(source, '__tn__'): # Table
                # Use Table's own string representation which handles quoting and aliasing
                _from = str(source)
            else:
                 raise ArgumentError(f"FROM expects string, Query, or Table, got {type(source)}")

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
            if isinstance(arg, str): cols.append(arg)
            else: cols.append(str(arg))
            
        if cols: self._state.groups.extend(cols)
        return self

    def INSERT_INTO(self, table: str, *args):
        this = self._clone()
        this._consequence = DML
        this._insert_args = len(args) # only available when insert into is the sql command
        this._callstack.append(INSERT_INTO_)
        this._pause_cloning = True
        
        this._chain_state()
        this._state.statement_type = 'INSERT'

        if isinstance(table, Table): t = table.__tn__()
        else: t = f'"{table}"'
            
        this._state.insert_table = t
        
        # Flatten args
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            cols = list(args[0])
        else:
            cols = list(args)
        
        # Determine if cols are strings or Fields
        quoted_cols = []
        for c in cols:
            if isinstance(c, str):
                quoted_cols.append(f'"{c}"')
            else:
                quoted_cols.append(str(c))
            
        this._state.insert_columns = quoted_cols
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
            tablename = f'"{table}"'
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
        self._state.limit = count
        if offset is not None: self._state.offset = offset
        return self

    def ORDER_BY(self, *args):
        """
        Add ORDER BY clause to the query.

        Use negative prefix (-column) for descending order.
        
        """
        self._callstack.append('ORDER_BY')
        
        order_parts = []
        for arg in args:
            if isinstance(arg, str):
                if arg.startswith('-'):
                    order_parts.append(f"{arg[1:]} DESC")
                else:
                    order_parts.append(f"{arg} ASC")
            else:
                # Column/Field object
                order_parts.append(f"{str(arg)} ASC")
                
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
                col = str(arg)
            parsed.append(col)

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
            elif hasattr(arg, '__tn__'):
                # Table object -> SELECT *
                this._tablenames.add(arg.__tn__())
                cols.append("*") 
            elif hasattr(arg, 'compile'):
                # Compilable object (WindowFunction, etc.)
                cols.append(arg)
            elif hasattr(arg, 'table'):
                # Field object
                if arg.table:
                    this._tablenames.add(arg.table.__tn__())
                cols.append(str(arg))
            else:
                 # Fallback
                 cols.append(str(arg))
        else:
            unique_tablenames = set([this.get_tablename(table) for table in args])
            # Add found tables to tablenames
            for t in unique_tablenames:
                if t: this._tablenames.add(t)
            
            is_heterogeneous = len(unique_tablenames) > 1

            for member in args:
                if isinstance(member, str):
                    cols.append(member)
                elif hasattr(member, '__tn__'):
                    # Table object
                    this._tablenames.add(member.__tn__())
                    # For now select * from table in list
                    # Or we could expand columns if we knew them, but dynamic table doesn't know columns
                    cols.append(f"{member._alias or member._name}.*")
                elif hasattr(member, 'compile'):
                    # Compilable object (WindowFunction, etc.)
                    cols.append(member)
                elif hasattr(member, 'table'):
                    # Field object
                    if member.table:
                        this._tablenames.add(member.table.__tn__())
                    cols.append(str(member))
                else:
                    # Fallback for other objects
                    cols.append(str(member))

        this._state.selects = cols
        return this

    def SET(self, *args):
        self._callstack.append('SET')
        updates = []
        for ax in args:
            if hasattr(ax, 'compile'):
                updates.append(ax)
            elif isinstance(ax, (str, Number)):
                updates.append(ax)
            elif hasattr(ax, 'print'):
                updates.append(ax.print(self))
            else:
                 updates.append(str(ax))
        
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
        
        # Heuristic for detecting single row vs multiple rows
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
             elem = args[0]
             # Check if element 0 matches row structure (list/tuple)
             if elem and isinstance(elem[0], (list, tuple)):
                 # List of rows
                 self._state.insert_values.extend(elem)
             else:
                 # Single row passed as tuple/list
                 self._state.insert_values.append(elem)
        elif args and isinstance(args[0], (list, tuple)):
             # Multiple args, first is tuple -> assume multiple rows
             self._state.insert_values.extend(args)
        else:
             # Multiple atomic args or single atomic arg -> one row
             self._state.insert_values.append(args)

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
        
        # Use conditionator to get the string OR Condition object
        cond = self._conditionator(condition)
        self._state.wheres.append(cond)
        
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

    # Window Function Methods
    
    def PARTITION_BY(self, *args):
        """
        Create a WindowSpec with PARTITION BY clause.
        
        Use negative prefix (-column) for descending order in ORDER BY.
        
        Args:
            *args: Columns to partition by
        
        Returns:
            WindowSpec: Window specification object
        """
        partition_cols = []
        for arg in args:
            # Handle negative for descending in ORDER BY context
            arg_str = str(arg)
            if arg_str.startswith('-'):
                # Keep negative for ORDER BY processing in WindowSpec
                partition_cols.append(arg_str)
            else:
                partition_cols.append(arg_str)
        
        return WindowSpec(partition_by=partition_cols)
    
    def WINDOW(self, name: str, spec: WindowSpec):
        """
        Define a named window specification.
        
        Args:
            name: Window name
            spec: WindowSpec object
        
        Returns:
            Query: self for method chaining
        """
        self._state.window_definitions[name] = spec
        return self
    
    # Ranking Window Functions
    
    def ROW_NUMBER(self):
        """ROW_NUMBER() window function."""
        return _ROW_NUMBER()
    
    def RANK(self):
        """RANK() window function."""
        return _RANK()
    
    def DENSE_RANK(self):
        """DENSE_RANK() window function."""
        return _DENSE_RANK()
    
    def NTILE(self, n: int):
        """NTILE(n) window function."""
        return _NTILE(n)
    
    def PERCENT_RANK(self):
        """PERCENT_RANK() window function."""
        return _PERCENT_RANK()
    
    def CUME_DIST(self):
        """CUME_DIST() window function."""
        return _CUME_DIST()
    
    # Value Window Functions
    
    def LAG(self, column, offset: int = 1, default=None):
        """
        LAG(column [, offset [, default]]) window function.
        
        Args:
            column: Column to get previous value from
            offset: Number of rows back (default 1)
            default: Default value if no previous row
        """
        return _LAG(column, offset, default)
    
    def LEAD(self, column, offset: int = 1, default=None):
        """
        LEAD(column [, offset [, default]]) window function.
        
        Args:
            column: Column to get next value from
            offset: Number of rows forward (default 1)
            default: Default value if no next row
        """
        return _LEAD(column, offset, default)
    
    def FIRST_VALUE(self, column):
        """FIRST_VALUE(column) window function."""
        return _FIRST_VALUE(column)
    
    def LAST_VALUE(self, column):
        """LAST_VALUE(column) window function."""
        return _LAST_VALUE(column)
    
    def NTH_VALUE(self, column, n: int):
        """NTH_VALUE(column, n) window function."""
        return _NTH_VALUE(column, n)
    
    # Aggregate Window Functions
    
    def SUM(self, column):
        """
        SUM(column) - can be used as aggregate or window function.
        
        When used with .OVER(), becomes a window function.
        """
        return WindowSum(column)
    
    def AVG(self, column):
        """
        AVG(column) - can be used as aggregate or window function.
        
        When used with .OVER(), becomes a window function.
        """
        return WindowAvg(column)
    
    def COUNT(self, column):
        """
        COUNT(column) - can be used as aggregate or window function.
        
        When used with .OVER(), becomes a window function.
        """
        return WindowCount(column)
    
    def MIN(self, column):
        """
        MIN(column) - can be used as aggregate or window function.
        
        When used with .OVER(), becomes a window function.
        """
        return WindowMin(column)
    
    def MAX(self, column):
        """
        MAX(column) - can be used as aggregate or window function.
        
        When used with .OVER(), becomes a window function.
        """
        return WindowMax(column)


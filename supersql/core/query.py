from asyncio import run
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from threading import Event
from numbers import Number

from typing import Union

from supersql.errors import (
    ArgumentError,
    MissingArgumentError,
    MissingCommandError,
    DatabaseError
)

from .database import Database
from .table import Table
from .results import Results

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

    def __init__(self, engine, dsn=None, user=None, password=None, host=None, port=None, database=None, silent=True, unsafe=False):
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
        """
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
        self._sql = []

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

        _params = {"host": host, "port": port, "user": user, "password": password, "database": database}
        self._db = Database(self, **_params)

    def _clone(self) -> "Query":
        """
        # ! Why copy of Query object is returned
        # A copy of query is returned so internal query variables do not
        # leak out to other query objects.
        #
        # i.e. it is possible to declare a global query object with connection
        # configuration and reuse without fear of internal state corruption
        """
        return type(self)(
            engine=self._engine,
            dsn=self._dsn,
            user=self._user,
            password=self._password,
            host=self._host,
            silent=self._silent,
            port=self._port,
            database=self._database,
            unsafe=self._unsafe
        ) if not self._pause_cloning else self

    def _conditionator(self, condition):
        if isinstance(condition, str):
            return f" {condition}"
        else:
            try:
                # NOTE: condition here is most likely Base instance and we can get values etc out of it???? maybe???
                # for using in $1, $2, $3 etc variable replacements
                # we can use a dict? to save column and get values for each - sleepy so do this when brain is fresh
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
        return self._database

    def execute(self, *args, **kwargs):
        """
        Flushes the SQL command to the server for execution

        ..raises:
        {ConnectionError} On failed connection attempts to the database engine

        {StatementError} When the SQL Statement is malformed i.e. before being
            sent to the database engine and only if `silent = False`
        
        {CommandError} When the database server could not execute the command
            sent from preparation of your query. Wraps the message of the
            database server internally for easy debugging.
        """
        async def wait():
            pass
        pass

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
        return "".join(self._sql)
    
    async def run(self, *args, **kwargs) -> Results:
        # probably want to append `;` f'{self._sql};' here?
        async with self._db as db:
            results = await db.executes(self)
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
            raise SQLError(msg)
    
    def AND(self, condition):
        self._sql.append(_AND)
        sql_snippet = self._conditionator(condition)
        self._sql.append(sql_snippet)
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
        this._sql.append('BEGIN')
        return this
    
    def COMMIT(self):
        self._pause_cloning = False
        self._callstack.append('COMMIT')
        self._sql.append(f'{self._t_}COMMIT;')
        self._t_ = ''  # reset here not necessary but hey...
        return self

    def DELETE(self, table):
        return self.DELETE_FROM(table)

    def DELETE_FROM(self, table):
        this = self._clone()
        this._callstack.append(DELETE)
        if isinstance(table, str):
            tablename = table
        elif isinstance(table, Table):
            tablename = table.__tn__()
        
        this._tablenames.add(tablename)
        sqlstatement = f'{this._t_}DELETE FROM {tablename}'
        this._sql.append(sqlstatement)
        return this

    def FETCH(self, *args):
        return self

    def FROM(self, *args, **kwargs):
        """
        Adds the left and right spaced _FROM_ constant to the pseudo call stack first
        then evaluates the argument(s) passed in for type
        to resolve the tablename and alias i.e. _from_ `abc as alias, bdd as alias`
        or _from_ `abc` before appending that to the _sql array
        """
        self._callstack.append(_FROM_)

        num_of_args = len(args)
        num_of_tables = len(self._tablenames)
        # msg = f"Found different tables in SELECT statement but only 1 command received in FROM"
        msg = f"tables:{num_of_tables}, args:{num_of_args}"

        if num_of_args != num_of_tables and num_of_tables > 0:
            raise MissingArgumentError(msg)

        for source in args:
            has_alias = None
            if isinstance(source, str):
                _a = None
                _q = source
            elif isinstance(source, Query):
                _a = source._alias
                _q = f"({source.print()})"
            elif isinstance(source, Table):
                _a = source._alias
                _q = source.__tn__()

            _from = f"{_q} AS {_a}" if _a and num_of_tables > 1 else f"{_q}"
            self._from.append(_from)

        _sql = ", ".join(
            [f"{table}" for table in self._from]
        ) if len(self._from) > 1 else "".join(table for table in self._from)
        self._sql.extend([_FROM_, _sql])

        return self

    def GROUP_BY(self, *args):
        return self

    def INSERT_INTO(self, table: str, *args):
        this = self._clone()
        this._consequence = DML
        this._insert_args = len(args) # only available when insert into is the sql command
        this._callstack.append(INSERT_INTO_)
        this._pause_cloning = True

        if isinstance(table, Table):
            t = table.__tn__()
        else:
            t = table

        sql_ = f"{this._t_}{INSERT_INTO_}{t}"
        sql_ = f"{sql_} ({', '.join(*args)})" if len(args) > 0 else sql_
        this._sql.append(sql_)
        return this

    def JOIN(self, *args):
        return self

    def LIMIT(self, *args):
        return self

    def ORDER_BY(self, *args):
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

        sql = ", ".join(parsed)
        self._sql.append(f' RETURNING {sql}')
        return self

    def SELECT(self, *args):
        this = self._clone()
        this._consequence = DQL
        this._callstack.append(SELECT)

        num_of_args = len(args)
        if num_of_args == 0:
            separator = "*"
        elif num_of_args == 1:
            arg = args[0]
            if isinstance(arg, str):
                _table = this.get_tablename(arg)
                this._tablenames.add(
                    _table
                ) if _table else this._orphans.add(arg)
                separator = arg
            elif isinstance(arg, Table):
                separator = "*"
                this._tablenames.add(arg.__tn__())
            else:
                separator = arg._name
                this._tablenames.add(arg._meta.__tn__())
        else:
            cols = []
            unique_tablenames = set([this.get_tablename(table) for table in args])
            is_heterogeneous = len(unique_tablenames) > 1

            for member in args:
                if isinstance(member, str):
                    _table = this.get_tablename(member)
                    this._tablenames.add(_table) if _table else None

                    cols.append(member)
                elif isinstance(member, Table):
                    # activate alias on tables if is_heterogeneous i.e.
                    # more than one table seen in select
                    if is_heterogeneous:
                        member.AS(member._alias if member._alias else member.__tn__())

                    this._tablenames.add(member.__tn__())
                    cols.extend(member.columns())
                else:
                    # Column object i.e. String, Int, Varchar etc.
                    alias = member._imeta._alias
                    tablename = member._imeta.__tn__()
                    member._imeta.AS(alias if alias else tablename)

                    this._tablenames.add(tablename)
                    if is_heterogeneous:
                        cols.append(f"{member._imeta._alias}.{member._name}")
                    else:
                        cols.append(f"{member._name}")

            separator = ", ".join(
                [col for col in cols]
            )

        # check if insert into is preceding this directly and not values or other command
        # we can then prevent the insertion of `; ` in such a case as it a continuation command
        is_inserting = len(this._callstack) > 1 and this._callstack[-2] == INSERT_INTO_
        _select_statement = f"{' ' if is_inserting else this._t_}SELECT {separator}"

        # if this._pristine:
        #     this._sql.append(_select_statement)
        #     this._pristine = False
        this._sql.append(_select_statement)
        return this

    def SET(self, *args):
        self._callstack.append('SET')

        self._sql.append(f'SET {", ".join(ax if isinstance(ax, (str, Number)) else ax.print(self) for ax in args)}')
        return self

    def UNION(self, *args):...

    def UPDATE(self, table):
        this = self._clone()
        this._consequence = DML
        this._callstack.append(UPDATE_)
        this._sql.append(f'{this._t_}{UPDATE_}{table if isinstance(table, str) else table.__tn__()} ')

        return this

    def UPSERT(self, *args):
        return self

    def VALUES(self, *args):
        # maybe validate len arg[args] matches the number of args provided if any in insert_into, maybe...
        self._callstack.append(VALUES_)
        vals = []

        def xfy(val):
            """Make vale sql friendly i.e. convert dates, booleans etc to sql types"""
            if isinstance(val, str): val = val.replace("'", "''") # should we escape single quotes by default
            elif isinstance(val, bool): val = 'true' if val else 'false'

            return f"{val}"

        for values in args:
            _wparens = ', '.join(f"'{xfy(value)}'" if isinstance(value, (str, bool)) else f"{value}" for value in values)
            sql = f"({_wparens})"
            vals.append(sql)

        sql = f" {VALUES_}{', '.join(vals)}"
        self._sql.append(sql)
        return self

    def WHERE(self, condition):
        """
        Check if _from was called and call it only if not a
        DELETE statement in play.

        Add WHERE constant to the pseudo call stack

        Process the `where ` condition by checking if condition is a
            - string: add as is with spaces as necessary
            - supersql datatype comparator: calls print() to get the SQL string repr.
        """
        if UPDATE_ in self._callstack: pass
        elif _FROM_ not in self._callstack:
            if DELETE not in self._callstack:
                tablenames = self._tablenames
                self = self.FROM(*tablenames)

        self._callstack.append(WHERE)
        self._sql.append(f" {WHERE}")
        sql_snippet = self._conditionator(condition)
        self._sql.append(sql_snippet)

        return self

    def WITHOUT(self, *args):...

    def WITH_RECURSIVE(self, *args):...

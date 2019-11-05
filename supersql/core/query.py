from supersql.core.table import Table
from supersql.errors import MissingArgumentError, MissingCommandError

from supersql.utils.helpers import get_tablename


SUPPORTED_VENDORS = (
    "postgres",
    "postgresql",
    "oracle",
    "oracledb",
    "mariadb",
    "mysql",
    "mssql",
    "sqlserver",
)

_SELECT = "SELECT"
_FROM = " FROM "
_WHERE = "WHERE"


class Query(object):
    """Query objects are the pipes through which ALL communication to
    the database is made.

    A query is the work horse for supersql as it is in SQL. Queries
    can be connected to the database or isolated and used for only
    generating vendor specific SQL strings.
    """

    def __init__(self, vendor, user=None, password=None, host=None, silent=True):
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
        if vendor not in SUPPORTED_VENDORS:
            raise NotImplementedError(f"{vendor} is not a supersql suppored engine")
        self._vendor = vendor
        self._user = user
        self._password = password
        self._host = host
        self._silent = silent
        self._print = []

        self._pristine = True
        self._disparity = 0  # how many tables is this query for?
        self._from = []
        self._callstack = []

        self._tablenames = set()
        self._orphans = set()
        self._alias = None
    
    @classmethod
    def clone(cls, q):
        """
        # ! Why copy of Query object is returned
        # A copy of query is returned so internal query variables do not
        # leak out to other query objects.
        #
        # i.e. it is possible to declare a global query object with connection
        # configuration and reuse without fear of internal state corruption
        """
        this = cls(
            vendor=q._vendor,
            user=q._user,
            password=q._password,
            host=q._host,
            silent=q._silent
        )
        return this
    
    def execute(self):
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
        pass
    
    def print(self):
        """
        Prints the current SQL statement as it exists on the query object

        ..return {str}  String representation of the SQL command to be sent
            to the database server if `execute` method is called.
        """
        return "".join(self._print)
    
    def was_called(self, command):
        return command in self._callstack
    
    def AS(self, alias):
        self._alias = alias
        return self

    def FROM(self, *args, **kwargs):
        """
        SQL FROM command proxy python method responsible for
        adding the `from` target of the query object.
        """
        # 1. If a query object i.e. q then it should be a copy and not the same
        # 2. str
        # 3. It can be a table object i
        self._callstack.append(_FROM)

        num_of_args = len(args)
        num_of_tables = len(self._tablenames)
        # msg = f"Found different tables in SELECT statement but only 1 command received in FROM"
        msg = f"tables:{num_of_tables}, args:{num_of_args}"

        if num_of_args != num_of_tables:
            raise MissingArgumentError(msg)
        
        for source in args:
            has_alias = None
            if isinstance(source, str):
                _a = None
                _q = str
            elif isinstance(source, Query):
                _a = source._alias
                _q = f"({source.print()})"
            elif isinstance(source, Table):
                _a = source._alias
                _q = source.__tn__()

            _from = f"{_q} AS {_a}" if _a else f"{_q}"
            self._from.append(_from)

        _sql = ", ".join(
            [f"{table}" for table in self._from]
        ) if len(self._from) > 1 else "".join(table for table in self._from)
        self._print.extend([_FROM, _sql])

        return self

    def SELECT(self, *args):
        """SQL SELECT Proxy
        Mechanism for selecting or specifying subset of data to select
        from a table, expression or subquery

        ```sql
            SELECT * FROM customers WHERE age > 10;
        ```

        ```py
            query = Query("postgres")
            query.SELECT("*").FROM("customers").WHERE("age > 10")

            # with table
            cust = Customer()
            query.SELECT(cust).FROM(cust).WHERE(cust.age > 10)

            # other possible ways to query with
            # a table object
            # from is omitted as it is obvious from `select`
            query.SELECT(cust).WHERE(cust.age > 10)

            # "*" can be omitted as it is default but FROM is no longer obvious
            query.SELECT().FROM(cust).WHERE(cust.age > 10)
        ```
        """
        this = Query.clone(self)

        this._callstack.append(_SELECT)

        num_of_args = len(args)
        if num_of_args == 0:
            separator = "*"
        elif num_of_args == 1:
            arg = args[0]
            if isinstance(arg, str):
                this._tablenames.add(
                    get_tablename(arg)
                ) if get_tablename(arg) != arg else this._orphans.add(arg)
                separator = arg
            elif isinstance(arg, Table):
                separator = "*"
                this._tablenames.add(arg.__tn__())
            else:
                separator = arg._name
                this._tablenames.add(arg._meta.__tn__())
        else:
            cols = []
            for member in args:
                if isinstance(member, str):
                    tablename = get_tablename(member)
                    this._tablenames.add(get_tablename(member)) if tablename != member else None
                    cols.append(member)
                elif isinstance(member, Table):
                    this._tablenames.add(member.__tn__())
                    cols.extend(member.columns())
                else:
                    this._tablenames.add(member._meta.__tn__())
                    cols.append(f"{member._meta.__tn__()}.{member._name}")

            separator = ", ".join(
                [col for col in cols]
            )

        _select_statement = f"SELECT {separator}"

        if this._pristine:
            this._print.append(_select_statement)
            this._pristine = False

        return this

    def WHERE(self, *args, **kwargs):
        if _FROM not in self._callstack:
            self = self.FROM()
        self._callstack.append(_WHERE)
        

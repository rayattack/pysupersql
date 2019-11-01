from supersql.core.table import Table


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
_FROM = "FROM"
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
        self._stack = []
    
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
        return command in self._stack

    def FROM(self, *args, **kwargs):
        self._stack.append(_FROM)

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
        self._stack.append(_SELECT)

        num_of_args = len(args)
        if num_of_args == 0:
            separator = "*"
        elif num_of_args == 1:
            arg = args[0]
            if isinstance(arg, str):
                separator = arg
            else:
                separator = "*" if isinstance(arg, Table) else arg._name
        else:
            cols = []
            self.uniformal = set()
            for member in args:
                if isinstance(member, str):
                    cols.append(member)
                elif isinstance(member, Table):
                    if member.__tablename__ not in self.uniformal:
                        self._disparity += 1
                    self.uniformal.add(member.__tablename__)
                    cols.extend(member.columns())
                else:
                    cols.append(f"{member._meta().__tablename__.lower()}.{member._name}")

            separator = ", ".join(
                [col for col in cols]
            )

        _select_statement = f"SELECT {separator}"

        if self._pristine:
            self._print.append(_select_statement)
            self._pristine = False

        return self

    def WHERE(self, *args, **kwargs):
        self._stack.append(_WHERE)
        if self.was_called(_FROM):
            pass


from supersql.errors import (
    ArgumentError,
    MissingArgumentError,
    MissingCommandError
)

from .database import Database
from .keywords import (
    FROM,
    WHERE,
    SELECT
)


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
        self._sql = []

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
    
    def database(self, name):
        """
        Get the database provided by name for inspection or operation
        """
        return Database()
    
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
        pass
    
    def print(self):
        """
        Prints the current SQL statement as it exists on the query object

        ..return {str}  String representation of the SQL command to be sent
            to the database server if `execute` method is called.
        """
        return "".join(self._sql)
    
    def run(self, *args, **kwargs):
        return self.execute(*args, **kwargs)
    
    def was_called(self, command):
        return command in self._callstack
    
    def AS(self, alias):
        """
        If select was last called then use this as the alias for select
        """
        self._alias = alias
        return self

    def DELETE(self, *args):...

    def DELETE_FROM(self, *args):...
    
    def FETCH(self, *args):...

    def FROM(self, *args, **kwargs):
        return FROM(*args, this=self)
    
    def GROUP_BY(self, *args):...

    def INSERT(self, *args):...

    def JOIN(self, *args):...
    
    def LIMIT(self, *args):...
    
    def ORDER_BY(self, *args):...

    def SELECT(self, *args):
        return SELECT(*args, this=Query.clone(self))
    
    def UNION(self, *args):...
    
    def UPDATE(self, *args):...

    def UPSERT(self, *args):...

    def WHERE(self, condition):
        return WHERE(this=self, condition=condition)
    
    def WITHOUT(self, *args):...

    def WITH_RECURSIVE(self, *args):...

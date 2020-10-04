"""
Results are what is returned after executing a query

Results are a collection of 1 or more `Row` objects, and rows
are akin to the [M]vc part of MVC i.e. model representation
of a single database row i.e. SELECT * FROM customers ORDER BY first_name LIMIT 10
will produce a Results Collection with 10 Result objects (result = 1 customer) results
= the set returned i.e. 10 customers.
"""
from supersql.errors import ProgrammingError


class Result(object):

    def __init__(self, *args, **kwargs):
        """Intialize result set and convert data from cursor/execution/db
        results to supersql iterable result set
        """
        _cursor = kwargs.get("cursor")
        if not _cursor:
            raise ProgrammingError
        self._columns = _cursor.description

    def __getitem__(self, keyname):
        pass

    def __setitem__(self, keyname, value):
        pass

    def autospect(self, table, values):
        pass

    def cell(self, row, col):
        """
        Returns the contents of the data that lives at the row/column coordinates
        using the non-zero based row number and column number, or the
        column name (as exists in the table, or alias if AS used in query)

        {row | int} Integer of the row to use as cursor point for data retrieval
            with support for -1 based syntax
        
        {col | int, str} Integer of col position in table or query if numeric
            argument otherwise name of col in table or alias if `AS` alias generator
            used in query
        """
        pass

    def column(self, col):
        """
        Returns an array of values for a single column i.e. all first_names, last_names
        from the result set

        {col | int, str}    Integer of col position in table/query, or name of column in
            table, or alias name used with query execution
        """
        pass

    @property
    def columns(self):
        """
        Return an ordered representation of column names
        """
        return [col.name for col in self._columns]

    @property
    def count(self):
        """
        Return the length of the result set
        """
        pass

    @property
    def headers(self):
        """
        Return the title of columns retrieved with the data
        """
        pass

    @property
    def rawdata(self):
        """
        Return the underlying result set as retrieved from the 
        driver/dbapi
        """
        pass

    def row(self, row):
        """
        Returns a row object. A Row is a mild representation of Models of
        MVC, however unlike models it has no bearing on persistence or
        querying of data. It is simply a representation of the data in
        object form with some utility helper methods.
        
        See `supersql.core.row.Row` for more details

        {row | int} The row number to fetch from the result set
        """
        pass

    def rows(self):
        """
        Returns an iterator of row objects that can be used to
        access mapped data
        """
        pass

    def to_csv(self, exclude=None, delimiter=','):
        """
        Save results as a CSV file
        """
        pass

    def to_dataframe(self):
        """
        Returns a pandas dataframe. Raises an ImportError if pandas library
        not found
        """
        # self.panda -> None raise error
        pass

    def to_dict(self, exclude=None):
        """
        Convert results to a python dictionary object excluding values
        in the exclude param for every row
        """
        pass

    def to_json(self, exclude=None):
        """
        Return JSON string represention of result set excluding
        values for columns in the exclude list.

        :param exclude: {list}
        Hybrid ist of column headers to exclude from json. List can
        contain both column indexes (integers) or names (strings)
        [0, 'first_name', 3, 'last_name'].
        Conflicts are ignored so 'first_name' and 1 will be condensed to exclude
        the same column without any issues
        """
        pass

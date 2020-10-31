"""
Row and Records classes representing data fetched from the database
after a query has been executed
"""


class Row(dict):
    def __init__(self, iterable=None):
        if not iterable:
            iterable = dict()
        self._data = iterable
        super().__init__(iterable)

    def __getitem__(self, keyname):
        value = self._data[keyname]
        if isinstance(value, dict):
            return type(self)(value)
        return value

    def __setitem__(self, keyname, value):
        self._data[keyname] = value

    def cell(self, col):
        """
        Returns the cell i.e. contents of the data at the provided col location
        
        {col | str,int} The column number or name
            (name in the table or alias given to the query)
        """
        pass


class Record(object):
    """A record is a collection of rows"""
    pass

"""
Schema classes specify the structure of a database
collection i.e. table view etal
"""


class Localcache(object):
    def __init__(self, *args, **kwargs):
        self._data = {}

    def __getattribute__(self, name):
        pass

    def __getitem__(self, name):
        return self[name]

    def __setitem__(self, name, value):
        self._data[name] = value


class Table(object):
    """Tables are representations of the primary data store i.e. Tables

    It is important to note that tables are not models as in SQLAlchemy
    and other ORMs. Tables are just that, representation of tables
    you can query, and they serve to define structure and properties
    of your actual database tables.

    When a table is queried it returns a `supersql.core.results.Results`
    object that contains a collection of rows matched by the query
    or nothing if no match was found by the database.

    Each result in the `Results` object is an instance of another
    supersql class `supersql.core.results.Result` and provides
    utility methods and properties that match the definitions
    in your table. I.e. if you define a custom table with a varchar(24)
    property called name, then result.name will return the value for that
    row and column combination i.e. Results.cell(row: int, col: str).
    """
    __tablename__ = None

    @classmethod
    def __autospector__(cls, *args, **kwargs):
        from supersql.datatypes.base import Base
        return {k: v for k, v in cls.__dict__.items() if isinstance(v, Base)}

    @classmethod
    def __tn__(cls):
        if cls.__tablename__:
            return cls.__tablename__.lower()
        return cls.__name__.lower()

    def __init__(self, *args, **kwargs):
        self._data = Localcache()
        _table = self.__tablename__ or type(self).__name__
        self.__tablename__ = _table.lower()

        self.fields_cache = self.__autospector__()
        self._alias = None
        self._args = []
        # self._alias = self.__tablename__  # default alias can be overriden by client

    def columns(self):
        _ = [self.fields_cache[k] for k in self.fields_cache]
        _ = sorted(_, key=lambda x: x._timestamp)

        # it table has an alias i.e. part of an heterogeneous collection or explicitly called
        # use it here otherwise just return the column name without fully qualified table name
        if self._alias:
            return [f"{self._alias}.{col._name}" for col in _]
        else:
            return [col._name for col in _]

    def get_field(self, name):
        return self._data.get(name)
    
    def AS(self, alias):
        self._alias = alias
        return self

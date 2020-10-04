from supersql.utils.pseudos import Cache


from .postgres import pgf


_PG = "postgres"


dialect_mapper = {
    _PG: pgf,
    "mysql": (),
    "mssql": (),
    "oracle": (),
    "mariadb": (),
    "mysql": (),
    "sqlite": (),
    "athena": ()
}

 
class Function(object):
    """
    Reflect the method name and the arguments passed in and return
    a string representation that can be used to generate an
    SQL query out of the box
    """
    def __init__(self, dialect=None):
        dialect = dialect or _PG
        self._function_library = dialect_mapper.get(dialect)

    def __getattr__(self, name):
        if name == "_function_library":
            return super.__getattr__(name)

        else:
            if name not in self._function_library:
                raise Exception

        def superwoman(*args):
            return Cache(name, args)

        return superwoman

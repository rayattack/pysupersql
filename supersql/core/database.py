

class Database(object):
    """Represents a database and its properties

    Supersql Database Objects are proxies to the actual database
    and serve primarily to access and configure database
    properties programatically.

    ..properties:

    name {str}: Name of the databas
    """

    def tables(self):
        """
        Returns a list of all the tables in the database.

        Each table in the tables collection corresponds to a supersql.core.table.Table
        instance object.

        Tables to be returned from the database are lazily loaded, that means
        the real table collection will be inspected upon access.
        """
        pass

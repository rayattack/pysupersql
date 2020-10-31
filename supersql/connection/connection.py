from importlib import import_module
from os import getenv

USER = 'SUPERSQL_DATABASE_USER'
HOST = 'SUPERSQL_DATABASE_HOST'
PORT = 'SUPERSQL_DATABASE_PORT'
PASSWORD = 'SUPERSQL_DATABASE_PASSWORD'
DATABASE = 'SUPERSQL_DATABASE_NAME'


_DEFAULT_PORTS = {
    "postgresql": 5432,
    "postgres": 5432,
    "mysql": 3306,
    "mssql": 1433,
}
_PORTLESS = ("oracle", "sqlite")


async def connect_and_execute(query):
    DatabaseDriver = import_module(query.vendor)

    async with DatabaseDriver.connect(query.database_url) as connection:
        async with connection.cursor() as cursor:
            return await cursor.execute(query.sql())


def _get_database_url(query):
    host = query.dbhost or getenv(HOST)
    user = query.dbuser or getenv(USER)
    database = getenv(DATABASE) or query.dbname

    port = getenv(PORT) or query._db_port or _default_ports.get(query.vendor)


class Connection(object):
    pass

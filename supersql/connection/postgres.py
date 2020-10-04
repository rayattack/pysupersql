import psycopg2


def connect(database, user, password, host, port):
    arguments = {
        "dbname": database,
        "user": user,
        "password": password,
        "host": host,
        "port": port,
    }
    return psycopg2.connect(**arguments)

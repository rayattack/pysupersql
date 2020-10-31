import sqlite3


def _connect(dbpath):
    connection = sqlite3.connect(dbpath)
    return connection


class Sqlite(object):
    def __init__(self, filename):
        self.filename = filename
    
    def __enter__(self):
        self.connection = sqlite3.connect(self.filename)
        return self.connection
    
    def __exit__(self, exctype, excvalue, traceback):
        self.connection.close()


# This is only useful for rolling back transactions not for connection closing
con = sqlite3.connect(':memory:')
con.execute('create table blah (id integer primary key, firstname varchar unique')
try:
    with con:
        con.execute('insert into blah(firstname) values (?)', ('Doofan',))
except sqlite3.IntegrityError:
    print('Duplicate record found in db')

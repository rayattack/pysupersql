import asyncpg


async def connect(**kwargs):
    connection = await asyncpg.connect(**kwargs)
    return connection


class Connection(object):
    def __init__(self, database):
        self._database = database
        self._connection = None
    
    def acquire(self):...
    def release(self):...
    def execute(self):...
    def run(self):...
    def find(self, limit=1):...
    


class Transaction(object):
    def __init__(self, connection):
        self._connection = connection
        self._transaction = None
    
    async def start(self):
        if not self._connection:
            raise ConnectionError('connection not available')
        self.transaction = self._connection.transaction()


class Postgres(object):
    async def connect(self):
        if self._connection_pool:
            raise ConnectionError('connection to db already established')
        self._connection_pool = await asyncpg.create_pool(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=self.database
        )
    
    async def disconnect(self):
        if not self._connection_pool:
            return
        await self._connection_pool.close()
        self._connection_pool = None

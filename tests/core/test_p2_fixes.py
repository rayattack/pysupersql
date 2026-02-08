import unittest
import asyncio
from supersql.core.query import Query
from supersql.engines.sqlite import Engine as SqliteEngine
from supersql.engines.postgres import Engine as PostgresEngine
from supersql.engines.mysql import Engine as MysqlEngine

class TestP2Fixes(unittest.IsolatedAsyncioTestCase):
    async def test_query_pool_args(self):
        """Test that Query accepts and stores pool arguments"""
        q = Query(
            'sqlite:///tmp/test.db',
            pool_min_size=5,
            pool_max_size=20,
            pool_timeout=45,
            pool_recycle=3600
        )
        self.assertEqual(q._pool_min_size, 5)
        self.assertEqual(q._pool_max_size, 20)
        self.assertEqual(q._pool_timeout, 45)
        self.assertEqual(q._pool_recycle, 3600)

    async def test_sqlite_pool_config(self):
        """Test that SQLite engine receives pool configuration"""
        q = Query(
            'sqlite:///tmp/test_pool.db',
            pool_min_size=2,
            pool_max_size=5,
            pool_timeout=10
        )
        # Force engine instantiation
        engine = q._db._engine
        self.assertIsInstance(engine, SqliteEngine)
        
        # Check if config was passed (implementation detail check)
        self.assertEqual(engine._config.get('pool_min_size'), 2)
        self.assertEqual(engine._config.get('pool_max_size'), 5)
        
        # Test connection structure
        await engine.connect()
        try:
            pool = engine.pool
            self.assertEqual(pool._min_size, 2)
            self.assertEqual(pool._max_size, 5)
            self.assertEqual(pool._timeout, 10)
            self.assertEqual(pool._queue.maxsize, 5)
            
            # Test acquire/release
            conn1 = await pool.acquire()
            self.assertIsNotNone(conn1)
            self.assertEqual(pool._current_size, 1)
            
            conn2 = await pool.acquire()
            self.assertIsNotNone(conn2)
            self.assertEqual(pool._current_size, 2)
            
            await pool.release(conn1)
            await pool.release(conn2)
            
        finally:
            await engine.disconnect()

    async def test_postgres_pool_args_passing(self):
        """Test that Postgres engine receives pool configuration"""
        q = Query(
            'postgres://user:pass@localhost:5432/db',
            pool_min_size=1,
            pool_max_size=3
        )
        engine = q._db._engine
        self.assertIsInstance(engine, PostgresEngine)
        self.assertEqual(engine._config.get('pool_min_size'), 1)
        self.assertEqual(engine._config.get('pool_max_size'), 3)

    async def test_mysql_pool_args_passing(self):
        """Test that MySQL engine receives pool configuration"""
        q = Query(
            'mysql://user:pass@localhost:3306/db',
            pool_min_size=4,
            pool_max_size=8
        )
        engine = q._db._engine
        self.assertIsInstance(engine, MysqlEngine)
        self.assertEqual(engine._config.get('pool_min_size'), 4)
        self.assertEqual(engine._config.get('pool_max_size'), 8)


import unittest
from supersql import Query, Table, Integer, String
from supersql.engines.sqlite import Engine

class Users(Table):
    id = Integer()
    name = String()

class TestP1Fixes(unittest.IsolatedAsyncioTestCase):
    async def test_sqlite_engine_connect_disconnect(self):
        """Test that SQLite engine can connect and disconnect"""
        q = Query('sqlite:///tmp/test.db')
        engine = q._db._engine
        
        self.assertIsNone(engine.pool)
        await engine.connect()
        self.assertIsNotNone(engine.pool)
        
        await engine.disconnect()
        # Pool should be None after disconnect
        self.assertIsNone(engine.pool)

    async def test_sqlite_query_generation(self):
        """Test that SQLite generic placeholders are used"""
        q = Query('sqlite:///tmp/test.db')
        u = Users()
        
        sql = q.SELECT(u.id).FROM(u).WHERE(u.id == 1).print()
        # Expected: id = ? (not $1)
        self.assertIn('id = ?', sql, f"Expected 'id = ?' in SQL, got: {sql}")

    async def test_postgres_query_generation(self):
        """Test that Postgres placeholders are still used"""
        q = Query('postgres://user:pass@localhost:5432/db')
        u = Users()
        
        sql = q.SELECT(u.id).FROM(u).WHERE(u.id == 1).print()
        self.assertIn('id = $1', sql, f"Expected 'id = $1' in SQL, got: {sql}")

    async def test_mysql_query_generation(self):
        """Test that MySQL placeholders are used"""
        try:
            q = Query('mysql://user:pass@localhost:3306/db')
            u = Users()
            
            sql = q.SELECT(u.id).FROM(u).WHERE(u.id == 1).print()
            self.assertIn('id = %s', sql, f"Expected 'id = %s' in SQL, got: {sql}")
        except ImportError:
            self.skipTest("aiomysql not installed")

    async def test_rollback_signature(self):
        """Test that rollback method exists and can be called"""
        q = Query('sqlite:///tmp/test.db')
        # Should not invoke error even if it does nothing
        await q._db.rollback()

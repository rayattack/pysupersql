"""
Real PostgreSQL connection tests.

These tests attempt to connect to an actual PostgreSQL database.
They will be skipped if the database is not available.
"""

import unittest
import asyncio
import os
from unittest import skipIf

from supersql import Query
from supersql.errors import VendorDependencyError


def postgres_available():
    """Check if PostgreSQL is available for testing."""
    try:
        import asyncpg
        return True
    except ImportError:
        return False


def database_accessible():
    """Check if the test database is accessible."""
    if not postgres_available():
        return False
    
    # Try to connect to the database
    try:
        async def test_connection():
            try:
                conn = await asyncpg.connect(
                    user="stationbot",
                    password="eldorad0",
                    host="localhost",
                    port=5432,
                    database="stationbase"
                )
                await conn.close()
                return True
            except Exception:
                return False
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(test_connection())
        finally:
            loop.close()
    except Exception:
        return False


class TestPostgresRealConnection(unittest.TestCase):
    """Test real PostgreSQL database connections."""
    
    def setUp(self):
        """Set up test configuration."""
        self.test_config = {
            "user": "stationbot",
            "password": "eldorad0",
            "host": "localhost",
            "port": 5432,
            "database": "stationbase"
        }
    
    @skipIf(not postgres_available(), "asyncpg not installed")
    def test_query_creation_with_postgres_dependencies(self):
        """Test that Query can be created with PostgreSQL when dependencies are available."""
        try:
            query = Query("postgres", **self.test_config)
            self.assertIsNotNone(query)
            self.assertEqual(query._engine, "postgres")
        except VendorDependencyError:
            self.fail("VendorDependencyError raised when asyncpg should be available")
    
    @skipIf(not database_accessible(), "PostgreSQL database not accessible")
    def test_real_database_connection(self):
        """Test actual connection to PostgreSQL database."""
        async def test_connection():
            query = Query("postgres", **self.test_config)
            
            try:
                async with query._db as db:
                    # If we get here, connection was successful
                    self.assertTrue(db.connected)
                    return True
            except Exception as e:
                self.fail(f"Failed to connect to PostgreSQL: {e}")
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(test_connection())
            self.assertTrue(result)
        finally:
            loop.close()
    
    @skipIf(not database_accessible(), "PostgreSQL database not accessible")
    def test_simple_query_execution(self):
        """Test executing a simple query against real database."""
        async def test_query():
            query = Query("postgres", **self.test_config)
            
            try:
                # Execute a simple query
                result = await query.sql("SELECT 1 as test_value")
                self.assertIsNotNone(result)
                return True
            except Exception as e:
                self.fail(f"Failed to execute query: {e}")
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(test_query())
            self.assertTrue(result)
        finally:
            loop.close()
    
    @skipIf(not database_accessible(), "PostgreSQL database not accessible")
    def test_connection_parameters_validation(self):
        """Test that connection parameters are correctly passed to asyncpg."""
        async def test_params():
            # Test with correct parameters
            query = Query("postgres", **self.test_config)
            
            async with query._db as db:
                self.assertTrue(db.connected)
            
            # Test with incorrect parameters should fail
            bad_config = self.test_config.copy()
            bad_config["password"] = "wrong_password"
            
            query_bad = Query("postgres", **bad_config)
            
            try:
                async with query_bad._db as db:
                    self.fail("Should have failed with wrong password")
            except Exception:
                # Expected to fail
                pass
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_params())
        finally:
            loop.close()
    
    def test_dsn_construction(self):
        """Test DSN construction from individual parameters."""
        query = Query("postgres", **self.test_config)
        
        # Verify the engine received the correct configuration
        engine_config = query._db._engine._config
        
        self.assertEqual(engine_config["user"], "stationbot")
        self.assertEqual(engine_config["password"], "eldorad0")
        self.assertEqual(engine_config["host"], "localhost")
        self.assertEqual(engine_config["port"], 5432)
        self.assertEqual(engine_config["database"], "stationbase")
    
    def test_connection_with_minimal_parameters(self):
        """Test connection with minimal required parameters."""
        # Test with just user and database (should use defaults for host/port)
        minimal_config = {
            "user": "stationbot",
            "password": "eldorad0",
            "database": "stationbase"
        }
        
        query = Query("postgres", **minimal_config)
        self.assertIsNotNone(query._db)
        
        # Verify defaults are not set in config (asyncpg will use its defaults)
        engine_config = query._db._engine._config
        self.assertEqual(engine_config.get("user"), "stationbot")
        self.assertEqual(engine_config.get("database"), "stationbase")
        # host and port should be None (asyncpg defaults)
        self.assertIsNone(engine_config.get("host"))
        self.assertIsNone(engine_config.get("port"))


class TestPostgresConnectionErrors(unittest.TestCase):
    """Test PostgreSQL connection error scenarios."""
    
    @skipIf(not postgres_available(), "asyncpg not installed")
    def test_connection_with_invalid_host(self):
        """Test connection failure with invalid host."""
        async def test_invalid_host():
            query = Query("postgres",
                         user="stationbot",
                         password="eldorad0",
                         host="invalid_host_that_does_not_exist",
                         database="stationbase")
            
            try:
                async with query._db as db:
                    self.fail("Should have failed with invalid host")
            except Exception:
                # Expected to fail
                pass
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_invalid_host())
        finally:
            loop.close()
    
    @skipIf(not postgres_available(), "asyncpg not installed")
    def test_connection_with_invalid_port(self):
        """Test connection failure with invalid port."""
        async def test_invalid_port():
            query = Query("postgres",
                         user="stationbot",
                         password="eldorad0",
                         host="localhost",
                         port=9999,  # Invalid port
                         database="stationbase")
            
            try:
                async with query._db as db:
                    self.fail("Should have failed with invalid port")
            except Exception:
                # Expected to fail
                pass
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_invalid_port())
        finally:
            loop.close()


if __name__ == '__main__':
    # Print information about test environment
    print(f"PostgreSQL dependencies available: {postgres_available()}")
    print(f"Test database accessible: {database_accessible()}")
    
    unittest.main(verbosity=2)

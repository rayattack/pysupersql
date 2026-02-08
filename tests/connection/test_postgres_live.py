"""
Live PostgreSQL connection tests with actual database.

These tests validate that SuperSQL can successfully connect to and interact
with a real PostgreSQL database using the provided credentials:
- User: stationbot
- Password: eldorad0
- Database: stationbase
- Host: localhost
- Port: 5432
"""

import unittest
import asyncio
import asyncpg
from supersql import Query
from supersql.errors import VendorDependencyError


class TestPostgresLiveConnection(unittest.TestCase):
    """Test live PostgreSQL database connections."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test configuration."""
        cls.test_config = {
            "user": "stationbot",
            "password": "eldorad0",
            "host": "localhost",
            "port": 5432,
            "database": "stationbase"
        }
    
    def test_direct_asyncpg_connection(self):
        """Test that direct asyncpg connection works with provided credentials."""
        async def test_connection():
            try:
                conn = await asyncpg.connect(**self.test_config)
                await conn.close()
                return True
            except Exception as e:
                self.fail(f"Direct asyncpg connection failed: {e}")
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(test_connection())
            self.assertTrue(result)
        finally:
            loop.close()
    
    def test_supersql_query_creation(self):
        """Test SuperSQL Query object creation with PostgreSQL."""
        try:
            query = Query("postgres", **self.test_config)
            
            # Verify all parameters are set correctly
            self.assertEqual(query._engine, "postgres")
            self.assertEqual(query._user, "stationbot")
            self.assertEqual(query._password, "eldorad0")
            self.assertEqual(query._host, "localhost")
            self.assertEqual(query._port, 5432)
            self.assertEqual(query._database, "stationbase")
            
        except VendorDependencyError:
            self.fail("VendorDependencyError raised when asyncpg should be available")
        except Exception as e:
            self.fail(f"Query creation failed: {e}")
    
    def test_supersql_database_connection(self):
        """Test SuperSQL database connection establishment."""
        async def test_connection():
            try:
                query = Query("postgres", **self.test_config)
                
                async with query._db as db:
                    # Verify connection is established
                    self.assertTrue(db.connected)
                    
                    # Verify we can access the engine
                    self.assertIsNotNone(db._engine)
                    self.assertIsNotNone(db._engine.pool)
                
                # After context, should be disconnected
                self.assertFalse(query._db.connected)
                
            except Exception as e:
                self.fail(f"SuperSQL connection failed: {e}")
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_connection())
        finally:
            loop.close()
    
    def test_connection_with_postgresql_alias(self):
        """Test connection using 'postgresql' alias."""
        async def test_connection():
            try:
                query = Query("postgresql", **self.test_config)
                
                async with query._db as db:
                    self.assertTrue(db.connected)
                
            except Exception as e:
                self.fail(f"PostgreSQL alias connection failed: {e}")
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_connection())
        finally:
            loop.close()
    
    def test_multiple_connections(self):
        """Test multiple sequential connections."""
        async def test_connections():
            try:
                query = Query("postgres", **self.test_config)
                
                # First connection
                async with query._db as db1:
                    self.assertTrue(db1.connected)
                
                # Second connection
                async with query._db as db2:
                    self.assertTrue(db2.connected)
                
                # Both should work independently
                self.assertFalse(query._db.connected)
                
            except Exception as e:
                self.fail(f"Multiple connections failed: {e}")
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_connections())
        finally:
            loop.close()
    
    def test_connection_parameters_validation(self):
        """Test that connection parameters are properly validated."""
        # Test with correct parameters
        try:
            query = Query("postgres", **self.test_config)
            self.assertIsNotNone(query._db)
        except Exception as e:
            self.fail(f"Valid parameters should work: {e}")
        
        # Test with minimal parameters
        try:
            minimal_config = {
                "user": "stationbot",
                "password": "eldorad0",
                "database": "stationbase"
            }
            query = Query("postgres", **minimal_config)
            self.assertIsNotNone(query._db)
        except Exception as e:
            self.fail(f"Minimal parameters should work: {e}")
    
    def test_dsn_construction_from_parameters(self):
        """Test that DSN is properly constructed from individual parameters."""
        query = Query("postgres", **self.test_config)
        
        # Verify the engine received the correct configuration
        engine_config = query._db._engine._config
        
        expected_params = {
            "user": "stationbot",
            "password": "eldorad0",
            "host": "localhost",
            "port": 5432,
            "database": "stationbase"
        }
        
        for key, expected_value in expected_params.items():
            actual_value = engine_config.get(key)
            self.assertEqual(actual_value, expected_value, 
                           f"Parameter {key}: expected {expected_value}, got {actual_value}")


class TestPostgresConnectionValidation(unittest.TestCase):
    """Test connection validation and error handling."""
    
    def test_invalid_credentials_handling(self):
        """Test handling of invalid credentials."""
        async def test_invalid_connection():
            # Test with wrong password
            invalid_config = {
                "user": "stationbot",
                "password": "wrong_password",
                "host": "localhost",
                "port": 5432,
                "database": "stationbase"
            }
            
            query = Query("postgres", **invalid_config)
            
            try:
                async with query._db as db:
                    self.fail("Should have failed with wrong password")
            except Exception:
                # Expected to fail with authentication error
                pass
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_invalid_connection())
        finally:
            loop.close()
    
    def test_invalid_database_handling(self):
        """Test handling of invalid database name."""
        async def test_invalid_db():
            # Test with non-existent database
            invalid_config = {
                "user": "stationbot",
                "password": "eldorad0",
                "host": "localhost",
                "port": 5432,
                "database": "nonexistent_database"
            }
            
            query = Query("postgres", **invalid_config)
            
            try:
                async with query._db as db:
                    self.fail("Should have failed with invalid database")
            except Exception:
                # Expected to fail with database error
                pass
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_invalid_db())
        finally:
            loop.close()


if __name__ == '__main__':
    print("Running live PostgreSQL connection tests...")
    print("Credentials: user=stationbot, password=eldorad0, database=stationbase")
    print("=" * 60)
    
    unittest.main(verbosity=2)

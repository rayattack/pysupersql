"""
Tests for database reflection functionality.

These tests validate that SuperSQL can automatically discover table schemas
and create Table objects from existing database tables.
"""

import unittest
import asyncio
from supersql import Query


class TestDatabaseReflection(unittest.TestCase):
    """Test database reflection functionality."""
    
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
        cls.connection_string = "postgres://stationbot:eldorad0@localhost:5432/stationbase"
    
    def test_connection_string_parsing(self):
        """Test parsing of connection strings."""
        query = Query(self.connection_string)
        
        self.assertEqual(query._engine, "postgres")
        self.assertEqual(query._user, "stationbot")
        self.assertEqual(query._password, "eldorad0")
        self.assertEqual(query._host, "localhost")
        self.assertEqual(query._port, 5432)
        self.assertEqual(query._database, "stationbase")
        self.assertEqual(query._dsn, self.connection_string)
    
    def test_postgresql_alias_parsing(self):
        """Test that postgresql:// is mapped to postgres engine."""
        connection_string = "postgresql://stationbot:eldorad0@localhost:5432/stationbase"
        query = Query(connection_string)
        
        self.assertEqual(query._engine, "postgres")
    
    def test_database_property_access(self):
        """Test that database property is accessible."""
        query = Query("postgres", **self.test_config)
        
        self.assertTrue(hasattr(query, 'database'))
        self.assertTrue(hasattr(query.database, 'table'))
        self.assertTrue(hasattr(query.database, 'tables'))
    
    def test_table_reflection(self):
        """Test reflecting a single table."""
        async def run_test():
            query = Query(self.connection_string)
            
            async with query.database as db:
                # Reflect the messengers table
                messengers = await db.table('messengers')
                
                # Verify table properties
                self.assertEqual(messengers.__tablename__, 'messengers')
                self.assertTrue(hasattr(messengers, 'columns'))
                self.assertTrue(hasattr(messengers, 'fields_cache'))
                
                # Verify columns are accessible
                columns = messengers.columns()
                self.assertIsInstance(columns, list)
                self.assertGreater(len(columns), 0)
                
                # Test specific columns exist
                expected_columns = ['username', 'display_name', 'workspace', 'profile_id', 'online']
                for column in expected_columns:
                    self.assertIn(column, columns)
                    self.assertTrue(hasattr(messengers, column))
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_test())
        finally:
            loop.close()
    
    def test_all_tables_reflection(self):
        """Test reflecting all tables in the database."""
        async def run_test():
            query = Query(self.connection_string)
            
            async with query.database as db:
                # Get all tables
                tables = await db.tables()
                
                # Verify we got a dictionary of tables
                self.assertIsInstance(tables, dict)
                self.assertGreater(len(tables), 0)
                
                # Verify messengers table is included
                self.assertIn('messengers', tables)
                
                # Verify each table is a proper Table object
                for table_name, table_obj in tables.items():
                    self.assertTrue(hasattr(table_obj, '__tablename__'))
                    self.assertEqual(table_obj.__tablename__, table_name)
                    self.assertTrue(hasattr(table_obj, 'columns'))
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_test())
        finally:
            loop.close()
    
    def test_column_types_mapping(self):
        """Test that database types are correctly mapped to SuperSQL types."""
        async def run_test():
            query = Query(self.connection_string)
            
            async with query.database as db:
                messengers = await db.table('messengers')
                
                # Test specific column types
                from supersql.datatypes.string import String
                from supersql.datatypes.numeric import Integer
                from supersql.datatypes.boolean import Boolean
                
                # Check that columns have the right types
                self.assertIsInstance(messengers.username, String)
                self.assertIsInstance(messengers.display_name, String)
                self.assertIsInstance(messengers.profile_id, Integer)
                self.assertIsInstance(messengers.online, Boolean)
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_test())
        finally:
            loop.close()
    
    def test_table_existence_check(self):
        """Test checking if tables exist."""
        async def run_test():
            query = Query(self.connection_string)
            
            async with query.database as db:
                from supersql.reflection.inspector import DatabaseInspector
                inspector = DatabaseInspector(db)
                
                # Test existing table
                exists = await inspector.table_exists('messengers')
                self.assertTrue(exists)
                
                # Test non-existing table
                exists = await inspector.table_exists('nonexistent_table_12345')
                self.assertFalse(exists)
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_test())
        finally:
            loop.close()
    
    def test_multiple_connection_methods(self):
        """Test that both connection methods work identically."""
        async def run_test():
            # Method 1: Individual parameters
            query1 = Query("postgres", **self.test_config)
            
            # Method 2: Connection string
            query2 = Query(self.connection_string)
            
            # Both should work and return the same results
            async with query1.database as db1:
                tables1 = await db1.tables()
            
            async with query2.database as db2:
                tables2 = await db2.tables()
            
            # Should have the same tables
            self.assertEqual(set(tables1.keys()), set(tables2.keys()))
            
            # Should be able to reflect the same table
            async with query1.database as db1:
                messengers1 = await db1.table('messengers')
            
            async with query2.database as db2:
                messengers2 = await db2.table('messengers')
            
            # Should have the same columns
            self.assertEqual(messengers1.columns(), messengers2.columns())
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_test())
        finally:
            loop.close()


if __name__ == '__main__':
    print("Running database reflection tests...")
    print("Credentials: user=stationbot, password=eldorad0, database=stationbase")
    print("=" * 60)
    
    unittest.main(verbosity=2)

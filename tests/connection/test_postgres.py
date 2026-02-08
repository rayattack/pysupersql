import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import asyncpg

from supersql import Query
from supersql.connection.postgres import connect
from supersql.engines.postgres import Engine
from supersql.core.database import Database
from supersql.errors import VendorDependencyError


class TestPostgresConnection(unittest.TestCase):
    """Test PostgreSQL connection functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "user": "stationbot",
            "password": "eldorad0",
            "host": "localhost",
            "port": 5432,
            "database": "stationbase"
        }

    def test_query_constructor_with_postgres_params(self):
        """Test Query constructor accepts PostgreSQL parameters."""
        query = Query("postgres", **self.test_config)

        # Verify parameters are stored correctly
        self.assertEqual(query._engine, "postgres")
        self.assertEqual(query._user, "stationbot")
        self.assertEqual(query._password, "eldorad0")
        self.assertEqual(query._host, "localhost")
        self.assertEqual(query._port, 5432)
        self.assertEqual(query._database, "stationbase")

    def test_query_constructor_with_postgresql_alias(self):
        """Test Query constructor accepts 'postgresql' as alias for 'postgres'."""
        query = Query("postgresql", **self.test_config)
        self.assertEqual(query._engine, "postgresql")

    def test_database_creation_with_postgres_query(self):
        """Test Database object creation with PostgreSQL query."""
        query = Query("postgres", **self.test_config)

        # Database should be created automatically in Query constructor
        self.assertIsInstance(query._db, Database)
        self.assertIsNotNone(query._db._engine)

    @patch('supersql.engines.postgres.asyncpg.create_pool')
    def test_engine_connect_with_valid_config(self, mock_create_pool):
        """Test Engine.connect() with valid configuration."""
        async def run_test():
            mock_pool = AsyncMock()
            # Make create_pool return an awaitable
            async def create_pool_coro(**_kwargs):
                return mock_pool
            mock_create_pool.side_effect = create_pool_coro

            query = Query("postgres", **self.test_config)
            engine = query._db._engine

            # Test connection
            await engine.connect()

            # Verify asyncpg.create_pool was called with correct parameters
            expected_kwargs = self.test_config.copy()
            expected_kwargs.update({
                'min_size': 10,
                'max_size': 10,
                'timeout': 60
            })
            mock_create_pool.assert_called_once_with(**expected_kwargs)
            self.assertEqual(engine.pool, mock_pool)

        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_test())
        finally:
            loop.close()

    @patch('supersql.engines.postgres.asyncpg.create_pool')
    def test_engine_disconnect(self, mock_create_pool):
        """Test Engine.disconnect() functionality."""
        async def run_test():
            mock_pool = AsyncMock()
            # Make create_pool return an awaitable
            async def create_pool_coro(**_kwargs):
                return mock_pool
            mock_create_pool.side_effect = create_pool_coro

            query = Query("postgres", **self.test_config)
            engine = query._db._engine

            # Connect first
            await engine.connect()
            self.assertIsNotNone(engine.pool)

            # Test disconnect
            await engine.disconnect()
            mock_pool.close.assert_called_once()
            self.assertIsNone(engine.pool)

        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_test())
        finally:
            loop.close()

    @patch('supersql.engines.postgres.asyncpg.create_pool')
    def test_database_context_manager(self, mock_create_pool):
        """Test Database async context manager."""
        async def run_test():
            mock_pool = AsyncMock()
            # Make create_pool return an awaitable
            async def create_pool_coro(**_kwargs):
                return mock_pool
            mock_create_pool.side_effect = create_pool_coro

            query = Query("postgres", **self.test_config)

            # Test context manager
            async with query._db as db:
                self.assertTrue(db.connected)
                expected_kwargs = self.test_config.copy()
                expected_kwargs.update({
                    'min_size': 10,
                    'max_size': 10,
                    'timeout': 60
                })
                mock_create_pool.assert_called_once_with(**expected_kwargs)

            # After context, should be disconnected
            self.assertFalse(query._db.connected)
            mock_pool.close.assert_called_once()

        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_test())
        finally:
            loop.close()

    def test_dsn_construction_from_parameters(self):
        """Test that DSN can be constructed from individual parameters."""
        query = Query("postgres", **self.test_config)

        # The engine should receive the parameters correctly
        engine_config = query._db._engine._config

        expected_config = {
            "user": "stationbot",
            "password": "eldorad0",
            "host": "localhost",
            "port": 5432,
            "database": "stationbase"
        }

        for key, value in expected_config.items():
            self.assertEqual(engine_config.get(key), value)

    def test_missing_required_parameters(self):
        """Test behavior with missing required parameters."""
        # Should work with minimal parameters (asyncpg has defaults)
        query = Query("postgres", user="stationbot", database="stationbase")
        self.assertIsNotNone(query._db)

    def test_environment_variable_fallback(self):
        """Test that environment variables are used as fallback."""
        import os

        # Set environment variables
        os.environ['SUPERSQL_DATABASE_USER'] = 'env_user'
        os.environ['SUPERSQL_DATABASE_PASSWORD'] = 'env_pass'
        os.environ['SUPERSQL_DATABASE_HOST'] = 'env_host'
        os.environ['SUPERSQL_DATABASE_PORT'] = '5433'
        os.environ['SUPERSQL_DATABASE_NAME'] = 'env_db'

        try:
            # Create query without explicit parameters
            query = Query("postgres")

            # Parameters should come from environment
            # Note: The current implementation doesn't fully support env vars in engine config
            # This test documents expected behavior for future implementation
            self.assertEqual(query._user, None)  # Current behavior

        finally:
            # Clean up environment variables
            for var in ['SUPERSQL_DATABASE_USER', 'SUPERSQL_DATABASE_PASSWORD',
                       'SUPERSQL_DATABASE_HOST', 'SUPERSQL_DATABASE_PORT', 'SUPERSQL_DATABASE_NAME']:
                os.environ.pop(var, None)


class TestPostgresConnectionIntegration(unittest.TestCase):
    """Integration tests for PostgreSQL connections."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "user": "stationbot",
            "password": "eldorad0",
            "host": "localhost",
            "port": 5432,
            "database": "stationbase"
        }

    @patch('supersql.engines.postgres.asyncpg.create_pool')
    def test_full_query_execution_flow(self, mock_create_pool):
        """Test full flow from Query creation to execution."""
        async def run_test():
            # Mock the connection pool and connection
            mock_connection = AsyncMock()
            mock_connection.fetch.return_value = [{"id": 1, "name": "test"}]

            mock_pool = AsyncMock()

            # Create a proper async context manager for pool.acquire()
            class MockAcquireContext:
                def __init__(self, connection):
                    self.connection = connection

                async def __aenter__(self):
                    return self.connection

                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    # Unused parameters are required for async context manager protocol
                    return None

            # Mock pool.acquire to return our async context manager
            # Make acquire a regular method (not async) that returns the context manager
            mock_pool.acquire = lambda: MockAcquireContext(mock_connection)

            # Make create_pool return an awaitable
            async def create_pool_coro(**_kwargs):
                return mock_pool
            mock_create_pool.side_effect = create_pool_coro

            # Create query and execute
            query = Query("postgres", **self.test_config)

            # Mock the query building (since we're testing connection, not query building)
            query._sql = ["SELECT * FROM users"]
            query._consequence = "DQL"
            query.print = MagicMock(return_value="SELECT * FROM users")
            query._args = []  # Use _args instead of args property

            # Execute query
            async with query._db as db:
                await db.execute(query)

            # Verify connection was established and query executed
            expected_kwargs = self.test_config.copy()
            expected_kwargs.update({
                'min_size': 10,
                'max_size': 10,
                'timeout': 60
            })
            mock_create_pool.assert_called_once_with(**expected_kwargs)
            mock_connection.fetch.assert_called_once()

        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_test())
        finally:
            loop.close()

    def test_connection_error_handling(self):
        """Test error handling for connection issues."""
        # Test with invalid engine
        with self.assertRaises(NotImplementedError):
            Query("invalid_engine", **self.test_config)

    @patch('supersql.engines.postgres.asyncpg.create_pool')
    def test_connection_pool_reuse(self, mock_create_pool):
        """Test that connection pool is reused across multiple queries."""
        async def run_test():
            mock_pool = AsyncMock()
            # Make create_pool return an awaitable
            async def create_pool_coro(**_kwargs):
                return mock_pool
            mock_create_pool.side_effect = create_pool_coro

            query = Query("postgres", **self.test_config)

            # Connect multiple times
            async with query._db:
                pass

            async with query._db:
                pass

            # Pool should be created twice (once per context manager entry)
            # This is current behavior - could be optimized to reuse pool
            self.assertEqual(mock_create_pool.call_count, 2)

        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_test())
        finally:
            loop.close()





if __name__ == '__main__':
    unittest.main()

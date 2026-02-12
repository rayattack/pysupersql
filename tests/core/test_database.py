import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from supersql.core.database import Database
from supersql.core.query import Query
from supersql.engines.connection import IEngine

# Mocking Engine parts as we need to test Database class behaviors
class MockEngine(IEngine):
    def __init__(self, query, **kwargs):
        self.pool = MagicMock()
    
    async def connect(self):
        pass
        
    async def disconnect(self):
        pass
        
    async def execute(self, sql):
        return []
    
    async def rollback(self):
        pass

@pytest.fixture
def mock_query():
    query = MagicMock(spec=Query)
    query._engine = 'postgres'
    query.build.return_value = "SELECT * FROM users"
    query._consequence = 'DQL'
    query._unsafe = False
    query.args = []
    # Explicitly attach _state and mock its attributes
    query._state = MagicMock() 
    query._state.statement_type = 'SELECT'
    return query

@pytest.fixture
def database(mock_query):
    # Patching the runtime_module_resolver to return our MockEngine
    with patch('supersql.core.database.Database.runtime_module_resolver') as mock_Resolver:
        mock_module = MagicMock()
        mock_module.Engine = MockEngine
        mock_Resolver.return_value = mock_module
        
        # Instantiate Database
        # Wait, Database constructor attempts to instantiate Engine immediately
        # So we need to ensure resolver returns the module correctly
        
        # Actually Database._get_engine_instance calls runtime_module_resolver(query._engine)
        # We need to mock that process
        
        db = Database(mock_query)
        # Replace the real engine with our mock (though init should have done it if patched correctly)
        db._engine = AsyncMock(spec=IEngine)
        db._engine.pool = MagicMock()
        
        yield db

@pytest.mark.asyncio
async def test_database_init(mock_query):
    with patch('supersql.core.database.Database.runtime_module_resolver') as mock_resolver:
        mock_module = MagicMock()
        mock_module.Engine = MockEngine
        mock_resolver.return_value = mock_module
        
        db = Database(mock_query)
        assert db is not None
        assert db.connected is False
        assert db._engine is not None

@pytest.mark.asyncio
async def test_database_connect_disconnect(database):
    # Test connect
    await database.connect()
    assert database.connected is True
    database._engine.connect.assert_called_once()
    
    # Test disconnect
    await database.disconnect()
    assert database.connected is False
    database._engine.disconnect.assert_called_once()

@pytest.mark.asyncio
async def test_database_context_manager(database):
    # Test async with
    async with database as db:
        assert db.connected is True
        database._engine.connect.assert_called_once()
        
    assert database.connected is False
    database._engine.disconnect.assert_called_once()

@pytest.mark.asyncio
async def test_database_execute_dql(database, mock_query):
    # Setup mock connection and acquisition
    mock_conn = AsyncMock()
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_conn
    mock_ctx.__aexit__.return_value = None
    database._engine.pool.acquire.return_value = mock_ctx
    
    # Mock query consequence DQL -> fetch
    mock_query._consequence = 'DQL'
    mock_conn.fetch.return_value = [{"id": 1, "name": "Test"}]
    
    results = await database.execute(mock_query)
    
    database._engine.pool.acquire.assert_called()
    mock_conn.fetch.assert_called_with("SELECT * FROM users")
    assert results is not None
    # Results(results) converts list of dicts/rows to Results object, let's just check length or existence
    # Wait, Results initialization implementation:
    # return Results(results)
    # Checking if it returns something
    assert len(results) == 1

@pytest.mark.asyncio
async def test_database_execute_dml(database, mock_query):
    # Setup mock connection
    mock_conn = AsyncMock()
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_conn
    mock_ctx.__aexit__.return_value = None
    database._engine.pool.acquire.return_value = mock_ctx
    
    # Mock query consequence DML -> fetchval (or execute depending on intent, execute implementation says fetchval for DML)
    mock_query._consequence = 'DML'
    mock_conn.fetchval.return_value = 1 # e.g. rowcount or inserted id
    
    val = await database.execute(mock_query)
    
    mock_conn.fetchval.assert_called_with("SELECT * FROM users")
    assert val == 1
    
@pytest.mark.asyncio
async def test_database_execute_other(database, mock_query):
    # DDL or other
    mock_conn = AsyncMock()
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_conn
    mock_ctx.__aexit__.return_value = None
    database._engine.pool.acquire.return_value = mock_ctx
    
    mock_query._consequence = 'DDL'
    mock_conn.execute.return_value = None
    
    await database.execute(mock_query)
    
    mock_conn.execute.assert_called_with("SELECT * FROM users")


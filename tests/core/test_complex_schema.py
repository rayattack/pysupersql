import json
from typing import TypedDict, Annotated, List, Dict
from supersql.core.schema import Schema
from supersql.core.results import Results
from supersql import Query
import pytest

# Define a nested TypedDict
class Address(TypedDict):
    city: str
    zipcode: str

# Define a complex schema
class UserProfile(Schema):
    id: int
    name: str  
    tags: Annotated[List[str], "min_len=1"]
    address: Address
    preferences: Dict[str, bool]

def test_complex_schema_validation():
    # 1. Valid Data
    valid_data = {
        "id": 1, 
        "name": "Jane", 
        "tags": ["admin", "staff"],
        "address": {"city": "New York", "zipcode": "10001"},
        "preferences": {"dark_mode": True, "notifications": False}
    }
    
    results = Results([valid_data], schema=UserProfile)
    row = results.row(1)
    
    # Check access
    assert row.name == "Jane"
    assert row.tags == ["admin", "staff"]
    assert row.address['city'] == "New York"
    
def test_complex_schema_invalid_data():
    # 2. Invalid Data (Empty list for tags, violates min_len=1)
    invalid_data = {
        "id": 2, 
        "name": "Bob", 
        "tags": [], # Error here
        "address": {"city": "Boston", "zipcode": "02108"},
        "preferences": {}
    }
    
    results = Results([invalid_data], schema=UserProfile)
    
    with pytest.raises(Exception) as excinfo:
        _ = results.row(1)
    
    # Pytastic error message usually contains the field name
    assert "tags" in str(excinfo.value) or "min_len" in str(excinfo.value)

def test_complex_schema_query_building():
    # 3. Query Building
    # We expect complex types to be treated as JSON columns in SQL generation
    db = Query('sqlite://:memory:')
    
    # We can query on scalar fields
    q = db.SELECT(UserProfile).FROM(UserProfile).WHERE(UserProfile.id == 1)
    sql = q.build()
    assert "id = 1" in sql or "id = ?" in sql or "id = $1" in sql or "id = %s" in sql
    
    # We might not strongly test JSON query syntax (e.g. ->>) as it varies by engine
    # and we just added basic JSON support. But basic selection should work.
    q2 = db.SELECT(UserProfile.address).FROM(UserProfile)
    assert "address" in q2.build()

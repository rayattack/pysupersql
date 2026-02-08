# Connecting to Databases

SuperSQL supports connecting to multiple database vendors with a consistent API. This guide shows you how to connect to different databases.

## Basic Connection Pattern

All database connections in SuperSQL follow the same pattern:

```python
from supersql import Query

query = Query(
    engine,           # Database vendor (required)
    user=user,        # Username (optional)
    password=password, # Password (optional)
    host=host,        # Host (optional)
    port=port,        # Port (optional)
    database=database # Database name (optional)
)
```

## Database-Specific Examples

### PostgreSQL

```python
from supersql import Query

# Basic connection
query = Query("postgres",
              user="postgres",
              password="password",
              host="localhost",
              port=5432,
              database="mydb")

# Using environment variables
import os
query = Query("postgres",
              user=os.getenv("DB_USER"),
              password=os.getenv("DB_PASSWORD"),
              host=os.getenv("DB_HOST", "localhost"),
              database=os.getenv("DB_NAME"))

# Connection string (if supported)
query = Query("postgres",
              dsn="postgresql://user:password@localhost:5432/mydb")
```

### MySQL

```python
from supersql import Query

# Basic connection
query = Query("mysql",
              user="root",
              password="password",
              host="localhost",
              port=3306,
              database="mydb")

# With SSL (recommended for production)
query = Query("mysql",
              user="root",
              password="password",
              host="localhost",
              database="mydb",
              use_ssl=True)
```

### SQL Server

```python
from supersql import Query

# Basic connection
query = Query("mssql",
              user="sa",
              password="password",
              host="localhost",
              port=1433,
              database="mydb")

# Windows Authentication
query = Query("mssql",
              host="localhost",
              database="mydb",
              trusted_connection=True)

# With specific driver
query = Query("mssql",
              user="sa",
              password="password",
              host="localhost",
              database="mydb",
              driver="ODBC Driver 17 for SQL Server")
```

### SQLite

```python
from supersql import Query

# File database
query = Query("sqlite", database="mydb.sqlite")

# Absolute path
query = Query("sqlite", database="/path/to/mydb.sqlite")

# In-memory database
query = Query("sqlite", database=":memory:")

# Relative path
query = Query("sqlite", database="./data/mydb.sqlite")
```

### Oracle

```python
from supersql import Query

# Basic connection
query = Query("oracle",
              user="system",
              password="password",
              host="localhost",
              port=1521,
              database="XE")

# Service name
query = Query("oracle",
              user="hr",
              password="password",
              host="localhost",
              port=1521,
              service_name="ORCL")

# TNS connection
query = Query("oracle",
              user="hr",
              password="password",
              tns="(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=ORCL)))")
```

## Connection Options

### Common Parameters

- `engine`: Database vendor (required)
- `user`: Database username
- `password`: Database password
- `host`: Database host (default: localhost)
- `port`: Database port (vendor-specific defaults)
- `database`: Database/schema name
- `dsn`: Connection string (if supported)

### Vendor-Specific Parameters

#### PostgreSQL
- `sslmode`: SSL mode (disable, allow, prefer, require)
- `application_name`: Application name for logging

#### MySQL
- `charset`: Character set (default: utf8mb4)
- `use_ssl`: Enable SSL connection
- `autocommit`: Auto-commit mode

#### SQL Server
- `driver`: ODBC driver name
- `trusted_connection`: Use Windows authentication
- `encrypt`: Enable encryption

#### SQLite
- `timeout`: Connection timeout
- `check_same_thread`: Thread safety check

## Environment Variables

SuperSQL automatically reads common environment variables:

```bash
export SUPERSQL_DATABASE_USER=myuser
export SUPERSQL_DATABASE_PASSWORD=mypassword
export SUPERSQL_DATABASE_HOST=localhost
export SUPERSQL_DATABASE_PORT=5432
export SUPERSQL_DATABASE_NAME=mydb
```

```python
# These will be used automatically
query = Query("postgres")
```

## Connection Pooling

SuperSQL uses connection pooling by default for better performance:

```python
# Connection pool is created automatically
query = Query("postgres", user="user", password="pass", database="db")

# Use async context manager for proper cleanup
async with query as q:
    results = await q.SELECT("*").FROM("users").run()
```

## Error Handling

### Connection Errors

```python
from supersql import Query
from supersql.errors import VendorDependencyError

try:
    query = Query("postgres", user="user", password="wrong")
    async with query as q:
        results = await q.SELECT("*").FROM("users").run()
except VendorDependencyError as e:
    print(f"Missing dependencies: {e}")
except ConnectionError as e:
    print(f"Connection failed: {e}")
except Exception as e:
    print(f"Other error: {e}")
```

## Best Practices

### 1. Use Environment Variables

```python
import os
from supersql import Query

query = Query("postgres",
              user=os.getenv("DB_USER"),
              password=os.getenv("DB_PASSWORD"),
              host=os.getenv("DB_HOST", "localhost"),
              database=os.getenv("DB_NAME"))
```

### 2. Use Async Context Managers

```python
async def get_users():
    async with query as q:
        return await q.SELECT("*").FROM("users").run()
```

### 3. Handle Vendor Dependencies

```python
from supersql.utils.vendor_deps import check_vendor_dependencies

vendor = "postgres"
installed, missing = check_vendor_dependencies(vendor)
if not installed:
    print(f"Install dependencies: pip install supersql[{vendor}]")
    exit(1)

query = Query(vendor, ...)
```

### 4. Configuration Management

```python
# config.py
DATABASE_CONFIG = {
    "postgres": {
        "user": "postgres",
        "password": "password",
        "host": "localhost",
        "database": "mydb"
    },
    "mysql": {
        "user": "root",
        "password": "password",
        "host": "localhost",
        "database": "mydb"
    }
}

# main.py
from supersql import Query
from config import DATABASE_CONFIG

def create_query(vendor):
    config = DATABASE_CONFIG[vendor]
    return Query(vendor, **config)
```

## Testing Connections

```python
async def test_connection(query):
    try:
        async with query as q:
            result = await q.sql("SELECT 1")
            print("Connection successful!")
            return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

# Test your connection
query = Query("postgres", user="user", password="pass", database="db")
await test_connection(query)
```
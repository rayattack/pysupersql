
# Connecting to Databases

Examples of connecting to different database vendors with SuperSQL.

## PostgreSQL

```python
from supersql import Query

# Basic connection
q = Query("postgres",
          user="postgres",
          password="postgres",
          host="localhost",
          port=5432,
          database="mydb")

# Using environment variables
import os
q = Query("postgres",
          user=os.getenv("DB_USER"),
          password=os.getenv("DB_PASSWORD"),
          host=os.getenv("DB_HOST", "localhost"),
          database=os.getenv("DB_NAME"))
```

## MySQL

```python
# MySQL connection
q = Query("mysql",
          user="root",
          password="password",
          host="localhost",
          port=3306,
          database="mydb")
```

## SQL Server

```python
# SQL Server connection
q = Query("mssql",
          user="sa",
          password="password",
          host="localhost",
          port=1433,
          database="mydb")
```

## SQLite

```python
# SQLite file database
q = Query("sqlite", database="mydb.sqlite")

# In-memory database
q = Query("sqlite", database=":memory:")
```

## Using Async Context Manager

```python
async def query_users():
    async with q as query:
        results = await query.SELECT("*").FROM("users").run()
        return results
```

## Error Handling

```python
from supersql.errors import VendorDependencyError

try:
    q = Query("postgres", user="user", password="pass")
except VendorDependencyError as e:
    print(f"Missing dependencies: {e}")
    # Install with: pip install supersql[postgres]
```

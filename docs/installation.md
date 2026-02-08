# Installation & Getting Started

SuperSQL is a Python library that provides a pythonic way to write SQL queries with support for multiple database vendors.

## Quick Installation

### Basic Installation

```bash
pip install supersql
```

This installs SuperSQL with minimal dependencies. You'll need to install vendor-specific dependencies separately based on which databases you plan to use.

### Vendor-Specific Installation

Install SuperSQL with support for specific database vendors:

```bash
# PostgreSQL support
pip install supersql[postgres]

# MySQL support  
pip install supersql[mysql]

# SQL Server support
pip install supersql[mssql]

# SQLite support
pip install supersql[sqlite]

# Oracle support
pip install supersql[oracle]

# Multiple vendors
pip install supersql[postgres,mysql,mssql]

# All vendors
pip install supersql[postgres,mysql,sqlite,mssql,oracle,oracledb,athena,presto]
```

## Supported Database Vendors

| Database | Extra Name | Required Dependencies | Status |
|----------|------------|----------------------|---------|
| PostgreSQL | `postgres` or `postgresql` | `asyncpg` | ✅ Full Support |
| MySQL | `mysql` | `aiomysql` | ✅ Full Support |
| MariaDB | `mariadb` | `aiomysql` | ✅ Full Support |
| SQL Server | `mssql` or `sqlserver` | `aioodbc`, `pyodbc` | ✅ Full Support |
| SQLite | `sqlite` | `aiosqlite` | ✅ Full Support |
| Oracle | `oracle` | `cx_Oracle` | ✅ Full Support |
| Oracle (modern) | `oracledb` | `oracledb` | ✅ Full Support |
| Amazon Athena | `athena` | `PyAthena` | 🚧 Experimental |
| Presto | `presto` | `presto-python-client` | 🚧 Experimental |

## First Steps

### 1. Import SuperSQL

```python
from supersql import Query, Table
```

### 2. Create a Query Object

```python
# For PostgreSQL
query = Query("postgres", 
              user="postgres", 
              password="password", 
              host="localhost", 
              database="mydb")

# For MySQL
query = Query("mysql",
              user="root",
              password="password", 
              host="localhost",
              database="mydb")

# For SQLite
query = Query("sqlite", database="mydb.sqlite")
```

### 3. Write Your First Query

```python
# Simple SELECT query
results = await query.SELECT("*").FROM("users").run()

# Or using async context manager
async with query as q:
    results = await q.SELECT("*").FROM("users").run()
```

## Error Handling

### Missing Dependencies

If you try to use a database vendor without installing its dependencies, SuperSQL provides helpful error messages:

```python
from supersql import Query

# This will raise a VendorDependencyError if asyncpg is not installed
query = Query("postgres")
```

**Error message:**
```
VendorDependencyError: Missing required dependencies for postgres: asyncpg
Install with: pip install supersql[postgres]
Or manually: pip install asyncpg
```

### Unsupported Vendors

```python
query = Query("unsupported_database")
```

**Error message:**
```
NotImplementedError: unsupported_database is not a supersql supported engine
```

## Development Installation

For development or contributing to SuperSQL:

```bash
# Clone the repository
git clone https://github.com/rayattack/supersql.git
cd supersql

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e .[postgres,mysql,sqlite,mssql,oracle]

# Or using Poetry
poetry install --extras "postgres mysql sqlite mssql oracle"
```

## Next Steps

- [Learn about vendor dependencies](vendor-dependencies.md)
- [Connect to your database](connecting.md)
- [Create table schemas](tables.md)
- [Write queries](query.md)
- [Work with results](results.md)

## Requirements

- Python 3.6+
- Database-specific drivers (installed automatically with vendor extras)

## License

SuperSQL is released under the MIT License. See the [LICENSE](https://github.com/rayattack/supersql/blob/main/LICENSE.md) file for details.

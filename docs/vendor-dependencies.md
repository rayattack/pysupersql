# Vendor Dependencies

SuperSQL uses optional dependencies for different database vendors. This approach keeps your installation lightweight while providing helpful error messages when dependencies are missing.

## Why Optional Dependencies?

- **Lightweight installations**: Only install drivers for databases you actually use
- **Clear error messages**: Get helpful installation instructions when dependencies are missing
- **Flexible deployment**: Different environments can have different database requirements
- **Better dependency management**: Avoid conflicts between database drivers

## Installation Options

### Single Vendor

```bash
# PostgreSQL only
pip install supersql[postgres]

# MySQL only
pip install supersql[mysql]

# SQL Server only
pip install supersql[mssql]
```

### Multiple Vendors

```bash
# PostgreSQL and MySQL
pip install supersql[postgres,mysql]

# Common web stack
pip install supersql[postgres,sqlite]

# Enterprise stack
pip install supersql[postgres,mssql,oracle]
```

### All Vendors

```bash
pip install supersql[postgres,mysql,sqlite,mssql,oracle,oracledb,athena,presto]
```

## Vendor Details

### PostgreSQL

**Extra names**: `postgres`, `postgresql`  
**Dependencies**: `asyncpg`

```bash
pip install supersql[postgres]
```

```python
from supersql import Query

query = Query("postgres",
              user="postgres",
              password="password",
              host="localhost",
              port=5432,
              database="mydb")
```

### MySQL / MariaDB

**Extra names**: `mysql`, `mariadb`  
**Dependencies**: `aiomysql`

```bash
pip install supersql[mysql]
```

```python
from supersql import Query

query = Query("mysql",
              user="root",
              password="password",
              host="localhost",
              port=3306,
              database="mydb")
```

### SQL Server

**Extra names**: `mssql`, `sqlserver`  
**Dependencies**: `aioodbc`, `pyodbc`

```bash
pip install supersql[mssql]
```

```python
from supersql import Query

query = Query("mssql",
              user="sa",
              password="password",
              host="localhost",
              port=1433,
              database="mydb")
```

### SQLite

**Extra name**: `sqlite`  
**Dependencies**: `aiosqlite`

```bash
pip install supersql[sqlite]
```

```python
from supersql import Query

query = Query("sqlite", database="mydb.sqlite")
# or in-memory
query = Query("sqlite", database=":memory:")
```

### Oracle

**Extra names**: `oracle`, `oracledb`  
**Dependencies**: `cx_Oracle` (legacy) or `oracledb` (modern)

```bash
# Modern Oracle driver (recommended)
pip install supersql[oracledb]

# Legacy Oracle driver
pip install supersql[oracle]
```

```python
from supersql import Query

query = Query("oracle",
              user="system",
              password="password",
              host="localhost",
              port=1521,
              database="XE")
```

## Error Handling

### Missing Dependencies Example

```python
from supersql import Query
from supersql.errors import VendorDependencyError

try:
    query = Query("postgres")
except VendorDependencyError as e:
    print(f"Error: {e}")
    # Output: Missing required dependencies for postgres: asyncpg
    # Install with: pip install supersql[postgres]
    # Or manually: pip install asyncpg
```

### Checking Dependencies Programmatically

```python
from supersql.utils.vendor_deps import (
    check_vendor_dependencies,
    get_vendor_dependencies,
    is_vendor_supported
)

# Check if vendor is supported
if is_vendor_supported("postgres"):
    print("PostgreSQL is supported")

# Get required dependencies
deps = get_vendor_dependencies("postgres")
print(f"PostgreSQL requires: {deps}")

# Check if dependencies are installed
installed, missing = check_vendor_dependencies("postgres")
if not installed:
    print(f"Missing dependencies: {missing}")
```

## Requirements Files

### requirements.txt

```txt
# Basic installation
supersql

# With PostgreSQL support
supersql[postgres]==2021.0.8

# With multiple vendors
supersql[postgres,mysql,sqlite]==2021.0.8
```

### pyproject.toml

```toml
[tool.poetry.dependencies]
python = "^3.6"
supersql = {extras = ["postgres", "mysql"], version = "^2021.0.8"}
```

### setup.py

```python
install_requires = [
    "supersql[postgres,mysql]>=2021.0.8",
]
```

## Docker Deployments

### Dockerfile Example

```dockerfile
FROM python:3.9-slim

# Install system dependencies for database drivers
RUN apt-get update && apt-get install -y \
    gcc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Install SuperSQL with required vendors
COPY requirements.txt .
RUN pip install -r requirements.txt

# Your app code
COPY . /app
WORKDIR /app
```

### requirements.txt for Docker

```txt
supersql[postgres,mysql]==2021.0.8
```

## Environment-Specific Installations

### Development

```bash
# Install all vendors for development
pip install supersql[postgres,mysql,sqlite,mssql,oracle]
```

### Production

```bash
# Install only what you need
pip install supersql[postgres]
```

### Testing

```bash
# SQLite for fast tests
pip install supersql[sqlite]
```

## Troubleshooting

### Common Issues

1. **ODBC Driver Missing** (SQL Server)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install unixodbc-dev
   
   # CentOS/RHEL
   sudo yum install unixODBC-devel
   ```

2. **Oracle Client Missing**
   ```bash
   # Download Oracle Instant Client
   # Set environment variables
   export ORACLE_HOME=/path/to/instantclient
   export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH
   ```

3. **MySQL Client Missing**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install default-libmysqlclient-dev
   
   # CentOS/RHEL
   sudo yum install mysql-devel
   ```

### Getting Help

If you encounter issues with vendor dependencies:

1. Check the [GitHub Issues](https://github.com/rayattack/supersql/issues)
2. Run the vendor dependencies demo: `python examples/vendor_dependencies_demo.py`
3. Verify your installation with the test script

## Migration from Previous Versions

If you're upgrading from a version without vendor dependencies:

1. **No breaking changes** - existing code continues to work
2. **Install vendor dependencies** - add the appropriate extras to your installation
3. **Update requirements** - specify vendor extras in your requirements files

### Before

```bash
pip install supersql
# All dependencies installed automatically
```

### After

```bash
pip install supersql[postgres]
# Only PostgreSQL dependencies installed
```

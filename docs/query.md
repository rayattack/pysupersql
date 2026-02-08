# Query API Reference

The `Query` class is the core of SuperSQL. It provides a fluent interface for building and executing SQL queries across multiple database vendors.

## Core Imports

```python
from supersql import Query, Table
from supersql import String, Integer, Date, UUID  # Data types
from supersql.errors import VendorDependencyError  # Error handling
```

## Query Object

The Query object serves as both a query builder and database connection manager. All database interactions happen through Query instances.


## Creating Query Objects

### Basic Query Creation

```python
from supersql import Query

# Database connection required (first parameter is engine)
query = Query("postgres",
              user="postgres",
              password="password",
              host="localhost",
              port=5432,
              database="mydb")
```

### Constructor Parameters

```python
Query(
    engine,           # Required: Database vendor
    dsn=None,         # Optional: Connection string
    user=None,        # Optional: Username
    password=None,    # Optional: Password
    host=None,        # Optional: Host (default: localhost)
    port=None,        # Optional: Port (vendor-specific defaults)
    database=None,    # Optional: Database name
    silent=True,      # Optional: Disable syntax checking
    unsafe=False      # Optional: Allow unsafe operations
)
```

### Supported Database Engines

| Engine | Aliases | Default Port | Dependencies |
|--------|---------|--------------|--------------|
| `postgres` | `postgresql` | 5432 | `asyncpg` |
| `mysql` | `mariadb` | 3306 | `aiomysql` |
| `mssql` | `sqlserver` | 1433 | `aioodbc`, `pyodbc` |
| `sqlite` | - | - | `aiosqlite` |
| `oracle` | `oracledb` | 1521 | `cx_Oracle` or `oracledb` |
| `athena` | - | - | `PyAthena` |
| `presto` | - | - | `presto-python-client` |

!!! info "Vendor Dependencies"
    Install vendor-specific dependencies with `pip install supersql[postgres]`.
    See [Vendor Dependencies](vendor-dependencies.md) for details.

### Environment Variables

SuperSQL automatically reads these environment variables:

```bash
export SUPERSQL_DATABASE_USER=myuser
export SUPERSQL_DATABASE_PASSWORD=mypassword
export SUPERSQL_DATABASE_HOST=localhost
export SUPERSQL_DATABASE_PORT=5432
export SUPERSQL_DATABASE_NAME=mydb
```

```python
# These will be used automatically if not provided
query = Query("postgres")
```

### Connection Examples

#### PostgreSQL
```python
query = Query("postgres",
              user="postgres",
              password="password",
              host="localhost",
              database="mydb")
```

#### MySQL
```python
query = Query("mysql",
              user="root",
              password="password",
              host="localhost",
              database="mydb")
```

#### SQL Server
```python
query = Query("mssql",
              user="sa",
              password="password",
              host="localhost",
              database="mydb")
```

#### SQLite
```python
query = Query("sqlite", database="mydb.sqlite")
# or in-memory
query = Query("sqlite", database=":memory:")
```

- *__dialect__*: What database dialect are you targeting. __`str`__
- *__user__*: The database user to connect as. __`str`__
- *__password__*: The database password for the provided user. __`str`__
- *__host__*: The IP address or hostname where the database lives with optional
    port information i.e. `localhost` or `localhost:5432` are both valid values. __`str`__
- *__port__*: Optional port information (ignored if port is found in `host` string). __`int`__
- *__database__*: The name of the target database on the host. __`str`__

&nbsp;



&nbsp;

## Query Command API

SuperSQL supports almost all SQL commands and the goal is to support all SQL commands
before v2020.1 comes out.

SQL commands supported as at v2019.3 includes:

- SELECT
- FROM
- WHERE
- GROUP_BY
- ORDER_BY
- AS
- IN
- JOIN
- HAVING
- LIMIT
- FETCH
- OFFSET
- BETWEEN
- FUNCTION
- WITH
- WITH_RECURSIVE
- UPSERT
- INSERT
- CREATE (tables, databases, extensions, views, triggers, schemas, functions etc.)
- DROP
- UPDATE
- AND
- OR
- CAST
- UNION
- UNION_ALL

For a full list of supported SQL constructs with code examples, see the examples section in the navigation.


## How Query Commands Work?

Every query object you create will have all the SQL commands functions as a python method with
CAPITALIZED method names, let us nickname these capitalized methods __`sqlproxies`__.

Perhaps it is more important to note that __`sqlproxies`__ are chainable and always return an
instance of the same query object with the exception of __SELECT__ and __WITH__ queries.

!!!note "SELECT, WITH, and WITH RECURSIVE returns a new Query instance"
    Whilst __`sqlproxies`__  return the same query object - __SELECT does not__.
    
    It creates a clone of the original query object so every select or subquery
    select has its own new slate from which to build and execute queries. This is necessary
    so you don't have to instantiate new query objects in subqueries.

    You can take a look at the implementation on github to see how SELECT differs from the
    other __`sqlproxies`__

```python
from supersql import Query

query = Query(...)  # connection params as required

emp = query.database("mydbname").tables().get("employee")

select_all = Query.SELECT().FROM(emp)
select_all_str = Query.SELECT("*").FROM("employee")
select_all_schema = Query.SELECT(emp).FROM(emp)

```


### Executing Queries

```py
from supersql import Query
from mycodebase.schemas import Employee

query = Query(...)
emp = Employee()

statement = query.SELECT(
    emp.first_name, emp.last_name, emp.age, emp.email
).FROM(
    emp
).WHERE(
    emp.email == "john.doe@example.org"
)

results = statement.execute()
```

Executing queries will return an `iterable` python object that is an instance of the
`supersql.core.result.Result` python class.


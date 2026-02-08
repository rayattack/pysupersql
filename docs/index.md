# Supersql : Made For Humans
In the process of building a SaaS product we investigated database tools for python and found amazing ones
like SQLAlchemy, PeeWee etc. However if you are like us your thought process might be:

1. But we don't want to use an ORM

2. Why can't we get a low level pythonic, powerful SQL API with with semantic interaction primitives

3. Async and Sync support should be supported

Supersql checks all those boxes and more. It is a python superset of SQL - allowing you leverage the full power of python to
write advanced SQL queries.


## Overview

There are 4 ways to query your data using SuperSQL

- Identifier Interpolation
- Manually create a _**Table**_ schema
- Automatically reflect tables from the database
- Use _`dict`_ and _`list`_ with **variables**


&nbsp;
#### Identifier Interpolation

```py
from os import environ
from supersql import Query

user = environ.get('DB_USER')
pwd = environ.get('DB_PWD')
dialect = environ.get('DB_ENGINE')

query = Query(vendor=dialect, user=user, password=pwd)

results = query.SELECT(
    "first_name", "last_name", "email"
).FROM(
    "employees"
).WHERE(
    "email = 'someone@example.com'"
).run()

```

!!!warning "Magic Literals Are Bad"
    It is usually not advisable to repeat string or other constants in multiple places across your codebase.
    If you notice string or literal values repeating more than once consider turning them into constants.


!!!info "Identifiers ONLY"
    It is advisable to limit use of strings to only identifiers e.g. `column names`, `table names`, `...`
    and operators `=`, `<>` etc.



&nbsp;
#### Manually Create Table Schema
```py
from supersql import Table
from supersql import (
    Date,
    Integer,
    String,
    UUID,
)


class Employee(Table):
    identifier = UUID(version=4)
    first_name = String(required=True)
    last_name = String(25)
    email = String(25, required=True, unique=True)
    age = Integer()
    created_on = Date()


emp = Employee()


results = query.SELECT(
    emp.first_name, emp.last_name, emp.email
).FROM(
    emp
).WHERE(
    emp.email == 'someone@example.com'
).execute()  # `execute` fetches all data into memory

```

!!!danger "Run vs Execute"
    `execute()` fetches all data into memory. Do not use with unsafe queries to large tables
    e.g. `SELECT * FROM very_large_table`. Use `run()` as it fetches data in chunks and
    reconnects as necessary to fetch more data.



&nbsp;
#### Auto-Reflect Table Schema
```py
...


tables = query.database("dbname").tables()
emp = tables.get("employees")


results = query.SELECT(
    emp.first_name, emp.last_name, emp.email
).FROM(
    emp
).WHERE(
    emp.email == 'someone@example.com'
).execute()

```

&nbsp;

#### Use Dict &amp; Lists with Variables
```py

from supersql import Query

query = Query(...)  # connection parameters as required

def example(table, *args, **kwargs)
    alt_results = query.SELECT(*args).FROM(table).WHERE(**kwargs).run()
```


&nbsp;
&nbsp;
## Okay... How about inserting Data?

Adding or inserting data with SuperSQL is just as easy as querying data.

However it is important for you to understand that __SuperSQL is NOT AN ORM__, and that means you
can't use some magical `table.save()` method to insert data to the database.

That's now how we roll... &nbsp; &nbsp; :smile:

So how then do you insert data? Let's look at some code.

```py
# borrowing Query and Employee code from above
...

def insert(**kwargs):
    result = query.INSERT(
        emp
    ).VALUES(
        **kwargs
    ).execute()


def bulk_insert(*args):
    result = query.INSERT(
        emp.first_name,
        emp.last_name,
        emp.email
    ).VALUES(
        args
    ).execute()


def insert_with_into(*args):
    # Use of INTO(table) used here is 100% optional but arguably
    # adds readability
    results = Query.INSERT(
        emp.first_name, emp.last_name, emp.email
    ).INTO(
        emp
    ).VALUES(
        ["John", "Doe", "john.doe@example.net"] if not args else args
    ).execute()

query.INSERT().INTO().VALUES().WHERE_NOT_EXISTS()
```


## Why SuperSQL?

- **Pythonic SQL**: Write SQL queries using Python syntax and objects
- **Multiple Database Support**: PostgreSQL, MySQL, SQL Server, SQLite, Oracle, and more
- **Async/Sync Support**: Built for modern async Python applications
- **Type Safety**: Leverage Python's type system for safer database operations
- **No ORM Overhead**: Direct SQL generation without ORM complexity
- **Vendor Dependencies**: Install only the database drivers you need


### Installation

```bash
# Install with PostgreSQL support
pip install supersql[postgres]

# Install with multiple database support
pip install supersql[postgres,mysql,sqlite]
```

### Your First Query

```python
from supersql import Query

# Connect to your database
query = Query("postgres",
              user="postgres",
              password="password",
              host="localhost",
              database="mydb")

# Write a query
results = await query.SELECT("*").FROM("users").WHERE("age > 18").run()

# Process results
for user in results:
    print(f"User: {user.name}, Age: {user.age}")
```


## Query Approaches

SuperSQL offers multiple ways to write queries, from simple string-based queries to fully typed table schemas:

### 1. String-Based Queries (Simple)

```python
from supersql import Query

query = Query("postgres", user="user", password="pass", database="db")

# Simple SELECT
results = await query.SELECT("first_name", "last_name", "email").FROM("employees").run()

# With WHERE clause
results = await query.SELECT("*").FROM("users").WHERE("age > 18").run()

# Complex query
results = await query.SELECT("u.name", "p.title").FROM("users u").JOIN("posts p ON u.id = p.user_id").run()
```

!!! warning "SQL Injection Risk"
    When using string-based queries, be careful about SQL injection. Use parameterized queries for user input.

### 2. Table Schema Approach (Recommended)

```python
from supersql import Query, Table
from supersql import String, Integer, Date, UUID

class Employee(Table):
    id = UUID(version=4)
    first_name = String(required=True)
    last_name = String(50)
    email = String(100, required=True, unique=True)
    age = Integer()
    hire_date = Date()

# Create query and table instance
query = Query("postgres", user="user", password="pass", database="db")
emp = Employee()

# Type-safe queries
results = await query.SELECT(
    emp.first_name, emp.last_name, emp.email
).FROM(emp).WHERE(
    emp.age > 18
).run()
```

!!! tip "Type Safety"
    Using table schemas provides type safety, IDE autocompletion, and prevents many common SQL errors.



### 3. Database Reflection (Auto-Discovery)

```python
# Automatically discover table schemas from the database
tables = await query.database("mydb").tables()
emp = tables.get("employees")

# Use reflected table
results = await query.SELECT(
    emp.first_name, emp.last_name, emp.email
).FROM(emp).WHERE(
    emp.email == 'someone@example.com'
).run()
```

### 4. Dynamic Queries with Variables

```python
def build_user_query(table, columns, filters):
    q = query.SELECT(*columns).FROM(table)

    for field, value in filters.items():
        q = q.WHERE(f"{field} = '{value}'")

    return q

# Usage
columns = ["name", "email", "age"]
filters = {"status": "active", "role": "admin"}
results = await build_user_query("users", columns, filters).run()
```

!!! info "Async vs Sync"
    SuperSQL is built for async Python. Use `await query.run()` for async execution.
    Sync support is available but async is recommended for better performance.



## Data Modification

SuperSQL supports all standard SQL operations: INSERT, UPDATE, DELETE.

### INSERT Operations

```python
from supersql import Query, Table
from supersql import String, Integer

class User(Table):
    name = String(100)
    email = String(100)
    age = Integer()

query = Query("postgres", user="user", password="pass", database="db")
user = User()

# Insert single record
await query.INSERT(user).VALUES(
    name="John Doe",
    email="john@example.com",
    age=30
).run()

# Insert multiple records
await query.INSERT(user).VALUES([
    {"name": "Alice", "email": "alice@example.com", "age": 25},
    {"name": "Bob", "email": "bob@example.com", "age": 35}
]).run()

# Insert with specific columns
await query.INSERT(user.name, user.email).VALUES(
    ("John Doe", "john@example.com"),
    ("Jane Doe", "jane@example.com")
).run()
```

### UPDATE Operations

```python
# Update with WHERE clause
await query.UPDATE(user).SET(
    name="John Smith",
    age=31
).WHERE(user.email == "john@example.com").run()

# Conditional update
await query.UPDATE(user).SET(
    age=user.age + 1
).WHERE(user.age < 65).run()
```

### DELETE Operations

```python
# Delete with WHERE clause
await query.DELETE().FROM(user).WHERE(user.age < 18).run()

# Delete all (be careful!)
await query.DELETE().FROM(user).run()
```

!!! warning "No ORM Magic"
    SuperSQL is NOT an ORM. There's no `user.save()` or `user.delete()` methods.
    All operations are explicit SQL operations, giving you full control.

## Key Features

### Async/Await Support

```python
# Async context manager (recommended)
async with query as q:
    results = await q.SELECT("*").FROM("users").run()

# Direct async calls
results = await query.SELECT("*").FROM("users").run()
```

### Connection Pooling

```python
# Connection pooling is automatic
query = Query("postgres", user="user", password="pass", database="db")

# Multiple queries reuse the connection pool
users = await query.SELECT("*").FROM("users").run()
posts = await query.SELECT("*").FROM("posts").run()
```

### Vendor Dependencies

```python
# Install only what you need
# pip install supersql[postgres]

from supersql.errors import VendorDependencyError

try:
    query = Query("postgres")
except VendorDependencyError as e:
    print(f"Missing dependencies: {e}")
    # Output: Missing required dependencies for postgres: asyncpg
    # Install with: pip install supersql[postgres]
```

## Next Steps

- [Installation & Setup](installation.md) - Get SuperSQL installed with your database
- [Vendor Dependencies](vendor-dependencies.md) - Learn about database-specific dependencies
- [Connecting to Databases](connecting.md) - Connect to your database
- [Table Schemas](tables.md) - Create type-safe table definitions
- [Writing Queries](query.md) - Master the query API
- [Working with Results](results.md) - Process query results

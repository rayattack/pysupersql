# SuperSQL: Made For Humans

**SuperSQL** is a Pythonic SQL query builder. It allows you to write SQL queries using the full power of Python objects and types, without the overhead or complexity of an ORM.

## Philosophy: Not an ORM

SuperSQL explicitly rejects the ORM (Object-Relational Mapping) pattern for the "Query Builder" pattern.
- **ORMs** (like Django, SQLAlchemy ORM) try to map database rows to Python objects with state, often hiding the actual SQL being executed.
- **SuperSQL** gives you a Python syntax that maps 1:1 to SQL commands.

You don't call `user.save()`. You write:
```python
await query.INSERT(User).VALUES(name="Alice").run()
```

You don't call `User.objects.filter(...)`. You write:
```python
await query.SELECT(User).FROM(User).WHERE(User.age > 18).run()
```

## Comparisons

| Feature | ORM (e.g. Django) | Raw SQL | SuperSQL |
|---------|-------------------|---------|----------|
| **Syntax** | Pythonic (Magic) | SQL String | Pythonic (Explicit) |
| **Type Safety** | High | None | High |
| **Control** | Low (Generated) | Full | Full |
| **Refactoring** | Easy | Hard | Easy (IDE support) |
| **Performance** | Variable (N+1 issues) | Best | Best (Direct SQL) |

## Quick Example

```python
from supersql import Query, Table

# 1. Connect
db = Query("postgres", database="mydb")

# 2. Define Table
users = Table("users")

# 3. Query
# "SELECT name FROM users WHERE age >= 21 AND active = true"
active_adults = await db.SELECT(
    users.name
).FROM(
    users
).WHERE(
    (users.age >= 21) & (users.active == True)
).run()
```

## Documentation Guide

*   [**Schema Definition**](tables.md): How to define tables/schemas for type safety.
*   [**Query Builder**](query.md): Comprehensive guide to SELECT, INSERT, UPDATE, DELETE, JOINs, CTEs, etc.
*   [**Data Types**](datatypes.md): Reference of all supported column types and validation rules.
*   [**Connections**](connecting.md): Connecting to PostgreSQL, MySQL, SQLite, etc.
*   [**Reflection**](reflection.md): Introspecting an existing database to generate code.


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

### 2. Dynamic Table Approach (Recommended)

```python
from supersql import Query, Table

# Create dynamic table references
users = Table("users")
posts = Table("posts")

# Create query instance
query = Query("postgres", user="user", password="pass", database="db")

# Type-safe queries with dynamic tables
results = await query.SELECT(
    users.first_name, users.last_name, users.email
).FROM(users).WHERE(
    users.age > 18
).run()

# With table aliases
u = Table("users").AS("u")
p = Table("posts").AS("p")

results = await query.SELECT(
    u.name, p.title
).FROM(u).JOIN(
    p, on=f"{u.id} = {p.user_id}"
).run()
```

!!! tip "Dynamic Tables"
    SuperSQL uses dynamic `Table` objects - no need to define schema classes. Access any column using dot notation, and SuperSQL handles the rest with proper identifier quoting.

### 3. Parameterized Queries (Security)

SuperSQL automatically parameterizes your queries to prevent SQL injection:

```python
users = Table("users")

# SECURE: Values are parameterized
age_threshold = 21  # User input
results = await query.SELECT(
    users.name, users.email
).FROM(users).WHERE(
    users.age >= age_threshold
).run()

# Generated SQL: SELECT "users"."name", "users"."email" FROM "users" WHERE "users"."age" >= $1
# Parameters: [21]
```

!!! success "SQL Injection Protection"
    All values in WHERE clauses, INSERT statements, and UPDATE operations are automatically parameterized using engine-specific placeholders (`$1` for PostgreSQL, `?` for SQLite, `%s` for MySQL).


### 4. Database Reflection (Auto-Discovery)

```python
# Automatically discover tables from database
tables = await query.database("mydb").tables()

# Or simply create dynamic table references
employees = Table("employees")

# Use dynamic table
results = await query.SELECT(
    employees.first_name, employees.last_name, employees.email
).FROM(employees).WHERE(
    employees.email == 'someone@example.com'
).run()
```

### 5. Dynamic Queries with Variables

```python
def build_user_query(table_name, columns, filters):
    table = Table(table_name)
    field_objects = [getattr(table, col) for col in columns]
    
    q = query.SELECT(*field_objects).FROM(table)
    
    for field, value in filters.items():
        # Automatically parameterized - safe from SQL injection
        q = q.WHERE(getattr(table, field) == value)
    
    return q

# Usage - all values are safely parameterized
columns = ["name", "email", "age"]
filters = {"status": "active", "role": "admin"}
results = await build_user_query("users", columns, filters).run()
```

!!! info "Async vs Sync"
    SuperSQL is built for async Python. Use `await query.run()` for async execution.
    Sync support is available but async is recommended for better performance.



## Data Modification

SuperSQL supports all standard SQL operations: INSERT, UPDATE, DELETE with automatic parameterization.

### INSERT Operations

```python
from supersql import Query, Table

users = Table("users")
query = Query("postgres", user="user", password="pass", database="db")

# Insert single record (values are parameterized)
await query.INSERT_INTO("users", "name", "email", "age").VALUES(
    "John Doe", "john@example.com", 30
).run()

# Or use Field objects for better clarity
await query.INSERT_INTO(users, users.name, users.email, users.age).VALUES(
    "John Doe", "john@example.com", 30
).run()

# Insert multiple records
await query.INSERT_INTO(users, users.name, users.email, users.age).VALUES(
    ("Alice", "alice@example.com", 25),
    ("Bob", "bob@example.com", 35)
).run()

# With RETURNING clause
result = await query.INSERT_INTO(
    users, users.name, users.email
).VALUES(
    "Jane Doe", "jane@example.com"
).RETURNING(users.id, users.created_at).run()
```

### UPDATE Operations

```python
# Update with WHERE clause (automatically parameterized)
await query.UPDATE(users).SET(
    users.name == "John Smith",
    users.age == 31
).WHERE(users.email == "john@example.com").run()

# Generated SQL: UPDATE "users" SET "name" = $1, "age" = $2 WHERE "users"."email" = $3
# Parameters: ["John Smith", 31, "john@example.com"]

# Conditional update with user input (safe from SQL injection)
min_age = 65  # User input
await query.UPDATE(users).SET(
    users.status == "senior"
).WHERE(users.age >= min_age).run()
```

### DELETE Operations

```python
# Delete with WHERE clause (parameterized)
min_age = 18  # User input - safely parameterized
await query.DELETE_FROM(users).WHERE(users.age < min_age).run()

# Delete all (be careful!)
await query.DELETE_FROM(users).run()
```

!!! warning "No ORM Magic"
    SuperSQL is NOT an ORM. There's no `user.save()` or `user.delete()` methods.
    All operations are explicit SQL operations with automatic parameterization for security.

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

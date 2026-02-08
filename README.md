# SuperSQL: SQL for Humans

**SuperSQL** is a powerful, pythonic SQL query builder that lets you write SQL using native Python objects.

It is **NOT an ORM**. There are no magic `.save()` methods, no hidden lazy-loading, and no confusing state management. You write explicit SQL queries (`SELECT`, `INSERT`, `UPDATE`) using a fluent Python API that looks and feels like SQL, but with the power of Python's type system and tooling.

---

### Features

-   **Pythonic Syntax**: Write SQL using chainable Python methods (`.SELECT().FROM().WHERE()`).
-   **Type Safe**: Define tables using Python classes for autocomplete and validation.
-   **Vendor Agnostic**: Support for PostgreSQL, MySQL, SQLite, Oracle, and SQL Server.
-   **Async & Sync**: Built for modern async Python (asyncio) but supports sync execution.
-   **No Magic**: You control the exact SQL being generated.
-   **Pytastic Integration**: Built-in schema validation using Pytastic.

---

### Installation

```bash
# Install with PostgreSQL support
pip install supersql[postgres]

# Or with all drivers
pip install supersql[postgres,mysql,sqlite]
```

### Quick Start

```python
from supersql import Query, Table

# 1. Connect to your database
query = Query("postgres", database="mydb")

# 2. Define your Table (Dynamic, no class needed!)
users = Table("users")

# 3. Write Pythonic SQL
# SELECT name, email FROM users WHERE age > 25
results = await query.SELECT(
    users.name, users.email
).FROM(
    users
).WHERE(
    users.age > 25
).run()
```

### Why SuperSQL?

SuperSQL gives you the power of a Query Builder without the overhead of an ORM.

1.  **Zero Boilerplate**: No need to define classes or duplicate your schema in Python.
2.  **Explicit Control**: You control the exact SQL execution.
3.  **Dynamic**: Works great with ad-hoc queries or evolving schemas.

---

[Read the Documentation](https://rayattack.github.io/supersql/)

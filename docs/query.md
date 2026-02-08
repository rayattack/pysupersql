# Query Builder

The `Query` object is your main entry point for building and executing SQL with automatic parameterization for security.

## Initialization

```python
from supersql import Query

# Postgres
db = Query('postgres', database='mydb', user='postgres', password='pass', host='localhost')

# SQLite
db = Query('sqlite:///my_db.sqlite')

# MySQL
db = Query('mysql', database='mydb', user='root', password='pass')
```

## SELECT

Use `.SELECT()` to choose columns. All queries are automatically parameterized for security.

```python
from supersql import Table

users = Table("users")

# SELECT * FROM "users"
await db.SELECT("*").FROM(users).run()

# SELECT "users"."name", "users"."email" FROM "users"  
await db.SELECT(users.name, users.email).FROM(users).run()

# With table alias
u = Table("users").AS("u")
await db.SELECT(u.name, u.email).FROM(u).run()
```

### Column Aliases

```python
# SELECT "users"."name" AS user_name FROM "users"
await db.SELECT(users.name.AS("user_name")).FROM(users).run()
```

## WHERE

Chain `.WHERE()` clauses for filtering. All values are automatically parameterized.

```python
# WHERE "users"."age" > $1 AND "users"."active" = $2
# Parameters: [18, True]
await db.SELECT(users.name).FROM(users).WHERE(
    users.age > 18
).WHERE(
    users.active == True
).run()

# User input is safely parameterized
age_input = 21  # From user
await db.SELECT(users.name).FROM(users).WHERE(
    users.age >= age_input
).run()
```

### Operators

Standard Python operators are overloaded for `Field` objects and return `Condition` objects:

| Operator | SQL | Example |
|----------|-----|---------|
| `==` | `=` | `users.age == 21` |
| `!=` | `<>` | `users.status != 'banned'` |
| `>` | `>` | `users.age > 18` |
| `>=` | `>=` | `users.score >= 100` |
| `<` | `<` | `users.balance < 0` |
| `<=` | `<=` | `users.attempts <= 3` |
| `&` | `AND` | `(users.age > 18) & (users.active == True)` |
| `|` | `OR` | `(users.role == 'admin') | (users.role == 'mod')` |
| `~` | `NOT` | `~(users.deleted == True)` |

### Special Methods

Field objects have special methods for advanced filtering:

```python
# IN - WHERE "users"."status" IN ($1, $2)
await db.SELECT("*").FROM(users).WHERE(
    users.status.IN(['active', 'pending'])
).run()

# NOT IN
await db.SELECT("*").FROM(users).WHERE(
    users.id.NOT_IN([1, 2, 3])
).run()

# LIKE - WHERE "users"."name" LIKE $1
await db.SELECT("*").FROM(users).WHERE(
    users.name.LIKE('A%')
).run()

# ILIKE (case-insensitive, PostgreSQL)
await db.SELECT("*").FROM(users).WHERE(
    users.email.ILIKE('%@gmail.com')
).run()

# BETWEEN - WHERE "users"."age" BETWEEN $1 AND $2
await db.SELECT("*").FROM(users).WHERE(
    users.age.BETWEEN(18, 65)
).run()

# IS NULL / IS NOT NULL
await db.SELECT("*").FROM(users).WHERE(users.deleted_at.IS_NULL())
await db.SELECT("*").FROM(users).WHERE(users.email.IS_NOT_NULL())
```

## JOIN

SuperSQL supports all standard SQL join types with automatic identifier quoting.

```python
users = Table("users")
posts = Table("posts")

# INNER JOIN "posts" ON "users"."id" = "posts"."user_id"
await db.SELECT(
    users.name, posts.title
).FROM(users).JOIN(
    posts, on=f"{users.id} = {posts.user_id}"
).run()

# Or use Condition objects for ON clause
await db.SELECT(
    users.name, posts.title
).FROM(users).JOIN(
    posts, on=(users.id == posts.user_id)
).run()
```

### Join Types

- `.JOIN(table, on=...)` - INNER JOIN (default)
- `.LEFT_JOIN(table, on=...)` - LEFT OUTER JOIN
- `.RIGHT_JOIN(table, on=...)` - RIGHT OUTER JOIN  
- `.FULL_JOIN(table, on=...)` - FULL OUTER JOIN
- `.CROSS_JOIN(table)` - CROSS JOIN (no ON clause)

## INSERT

INSERT operations automatically parameterize all values for security.

```python
users = Table("users")

# Single record - INSERT INTO "users" ("name", "age") VALUES ($1, $2)
# Parameters: ['Alice', 30]
await db.INSERT_INTO("users", "name", "age").VALUES('Alice', 30).run()

# Or use Field objects
await db.INSERT_INTO(users, users.name, users.email, users.age).VALUES(
    'Alice', 'alice@example.com', 30
).run()

# Multiple records
await db.INSERT_INTO(users, users.name, users.age).VALUES(
    ('Bob', 25),
    ('Charlie', 35)
).run()

# With RETURNING clause
result = await db.INSERT_INTO(users, users.name, users.email).VALUES(
    'Dave', 'dave@example.com'
).RETURNING(users.id, users.created_at).run()
```

## UPDATE

UPDATE operations are automatically parameterized.

```python
# UPDATE "users" SET "active" = $1 WHERE "users"."id" = $2
# Parameters: [True, 1]
await db.UPDATE(users).SET(
    users.active == True
).WHERE(users.id == 1).run()

# Multiple columns
await db.UPDATE(users).SET(
    users.name == "John Smith",
    users.age == 31
).WHERE(users.id == 1).run()

# User input is safely parameterized
new_status = "verified"  # From user
await db.UPDATE(users).SET(
    users.status == new_status
).WHERE(users.email == "user@example.com").run()
```

## DELETE

DELETE operations with parameterized WHERE clauses.

```python
# DELETE FROM "users" WHERE "users"."id" = $1
# Parameters: [1]
await db.DELETE_FROM(users).WHERE(users.id == 1).run()

# With user input (safely parameterized)
user_id = 42  # From user
await db.DELETE_FROM(users).WHERE(users.id == user_id).run()
```

## Common Table Expressions (CTEs)

Use `.WITH(alias, subquery)` to create CTEs for complex queries.

### Basic CTE

```python
users = Table("users")
orders = Table("orders")

# Create a CTE for active users
active_users_cte = db.SELECT(users.id, users.name).FROM(users).WHERE(
    users.active == True
)

# Use the CTE in main query
# WITH active_users AS (SELECT ...) SELECT * FROM active_users
result = await db.WITH("active_users", active_users_cte).SELECT(
    "*"
).FROM("active_users").run()
```

### Multiple CTEs

```python
# Chain multiple CTEs
high_value_orders = db.SELECT(orders.user_id).FROM(orders).WHERE(
    orders.total > 1000
)

active_users = db.SELECT(users.id, users.name).FROM(users).WHERE(
    users.active == True
)

# Use both CTEs
result = await db.WITH("high_value", high_value_orders).WITH(
    "active", active_users
).SELECT("*").FROM("high_value").JOIN(
    "active", on="high_value.user_id = active.id"
).run()
```

### Recursive CTEs

```python
# Employee hierarchy example
employees = Table("employees")

# Recursive CTE for organizational chart
hierarchy = """
SELECT id, name, manager_id, 1 as level
FROM employees
WHERE manager_id IS NULL
UNION ALL
SELECT e.id, e.name, e.manager_id, h.level + 1
FROM employees e
INNER JOIN hierarchy h ON e.manager_id = h.id
"""

result = await db.WITH("hierarchy", hierarchy).SELECT(
    "*"
).FROM("hierarchy").ORDER_BY("level").run()
```

## ORDER BY

```python
# ORDER BY "users"."age" ASC
await db.SELECT("*").FROM(users).ORDER_BY(users.age).run()

# Multiple columns
await db.SELECT("*").FROM(users).ORDER_BY(users.age, users.name).run()

# Descending (use '-' prefix for strings)
await db.SELECT("*").FROM(users).ORDER_BY("-age").run()
```

## LIMIT and OFFSET

```python
# LIMIT 10
await db.SELECT("*").FROM(users).LIMIT(10).run()

# LIMIT 10 OFFSET 20
await db.SELECT("*").FROM(users).LIMIT(10, offset=20).run()
```

## GROUP BY and HAVING

```python
# GROUP BY "users"."country"
await db.SELECT(users.country, "COUNT(*) as total").FROM(users).GROUP_BY(
    users.country
).run()

# With HAVING
await db.SELECT(users.country, "COUNT(*) as total").FROM(users).GROUP_BY(
    users.country
).HAVING("COUNT(*) > 10").run()
```

## Raw SQL

You can mix raw SQL strings with the query builder when needed:

```python
# Full raw query
await db.SELECT("*").FROM("users").WHERE("age > 18").run()

# Mixed - values still parameterized in WHERE using Field objects
await db.SELECT("*").FROM("users").WHERE(users.age > 18).run()
```

!!! warning "Parameterization"
    When using raw SQL strings in WHERE clauses, you must manually ensure they're safe from SQL injection. Use Field objects and operators for automatic parameterization.

## Transaction Support

```python
# Begin transaction
await db.BEGIN().run()

try:
    await db.INSERT_INTO(users, users.name).VALUES("Alice").run()
    await db.UPDATE(users).SET(users.balance == 100).WHERE(users.name == "Bob").run()
    await db.COMMIT().run()
except Exception:
    await db.ROLLBACK().run()
```

## Execution

All queries end with `.run()` for async execution:

```python
# Returns list of records
results = await query.SELECT("*").FROM(users).run()

# Iterate over results
for user in results:
    print(user.name, user.email)
```

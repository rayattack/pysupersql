# Filtering (WHERE)

Filtering in SuperSQL is done using Python expressions that compile to parameterized SQL, protecting against SQL injection.

## How Filtering Works

When you use operators on `Field` objects, SuperSQL creates `Condition` objects that:
1. Generate proper SQL syntax with identifier quoting
2. Extract values into parameters
3. Use engine-specific placeholders (`$1`, `?`, `%s`)

```python
from supersql import Query, Table

users = Table("users")
db = Query("postgres", database="mydb")

# This creates a Condition object
condition = users.age > 18

# When compiled, generates:
# SQL: "users"."age" > $1
# Parameters: [18]
```

## Basic Operators

All comparison operators are automatically parameterized:

| Python | SQL | Example | Generated SQL |
|--------|-----|---------|---------------|
| `==` | `=` | `users.age == 21` | `"users"."age" = $1` |
| `!=` | `<>` | `users.status != 'banned'` | `"users"."status" <> $1` |
| `>` | `>` | `users.age > 18` | `"users"."age" > $1` |
| `>=` | `>=` | `users.score >= 100` | `"users"."score" >= $1` |
| `<` | `<` | `users.balance < 0` | `"users"."balance" < $1` |
| `<=` | `<=` | `users.attempts <= 3` | `"users"."attempts" <= $1` |

### Usage Example

```python
# User input is automatically parameterized
age_threshold = 18  # Could be from user input
results = await db.SELECT("*").FROM(users).WHERE(
    users.age >= age_threshold
).run()

# Generated SQL: SELECT * FROM "users" WHERE "users"."age" >= $1
# Parameters: [18]
```

## Logical Operators

Combine conditions using `&` (AND), `|` (OR), and `~` (NOT):

| Python | SQL | Description |
|--------|-----|-------------|
| `&` | `AND` | Both conditions must be true |
| `|` | `OR` | Either condition must be true |
| `~` | `NOT` | Negates the condition |

```python
# AND - Both conditions must be true
await db.SELECT("*").FROM(users).WHERE(
    (users.age > 18) & (users.active == True)
).run()
# SQL: WHERE ("users"."age" > $1) AND ("users"."active" = $2)
# Parameters: [18, True]

# OR - Either condition can be true
await db.SELECT("*").FROM(users).WHERE(
    (users.role == 'admin') | (users.role == 'moderator')
).run()
# SQL: WHERE ("users"."role" = $1) OR ("users"."role" = $2)
# Parameters: ['admin', 'moderator']

# NOT - Negates condition
await db.SELECT("*").FROM(users).WHERE(
    ~(users.deleted == True)
).run()
```

## Special Operators

### IN / NOT IN

The `IN` operator checks if a value exists in a list. All values are parameterized:

```python
# IN with multiple values
await db.SELECT("*").FROM(users).WHERE(
    users.status.IN(["active", "pending", "verified"])
).run()
# SQL: WHERE "users"."status" IN ($1, $2, $3)
# Parameters: ['active', 'pending', 'verified']

# NOT IN
await db.SELECT("*").FROM(users).WHERE(
    users.id.NOT_IN([1, 2, 3])
).run()
# SQL: WHERE "users"."id" NOT IN ($1, $2, $3)
# Parameters: [1, 2, 3]

# With user input - safely parameterized
banned_ids = [10, 20, 30]  # From user/database
await db.SELECT("*").FROM(users).WHERE(
    users.id.NOT_IN(banned_ids)
).run()
```

### LIKE / ILIKE

Pattern matching with automatic parameterization:

```python
# LIKE - Case sensitive pattern matching
await db.SELECT("*").FROM(users).WHERE(
    users.name.LIKE("Al%")
).run()
# SQL: WHERE "users"."name" LIKE $1
# Parameters: ['Al%']

# ILIKE - Case insensitive (PostgreSQL only)
await db.SELECT("*").FROM(users).WHERE(
    users.name.ILIKE("al%")
).run()

# User search - safely parameterized
search_term = "john"  # User input
await db.SELECT("*").FROM(users).WHERE(
    users.name.LIKE(f"%{search_term}%")
).run()
```

### BETWEEN

Checks if value is within a range:

```python
# BETWEEN for age range
await db.SELECT("*").FROM(users).WHERE(
    users.age.BETWEEN(18, 65)
).run()
# SQL: WHERE "users"."age" BETWEEN $1 AND $2
# Parameters: [18, 65]

# With dates
await db.SELECT("*").FROM(orders).WHERE(
    orders.created.BETWEEN("2024-01-01", "2024-12-31")
).run()
```

### IS NULL / IS NOT NULL

Check for NULL values:

```python
# IS NULL
await db.SELECT("*").FROM(users).WHERE(
    users.deleted_at.IS_NULL()
).run()
# SQL: WHERE "users"."deleted_at" IS NULL

# IS NOT NULL
await db.SELECT("*").FROM(users).WHERE(
    users.email.IS_NOT_NULL()
).run()
# SQL: WHERE "users"."email" IS NOT NULL
```

## Complex Logic

Group conditions using parentheses for complex boolean logic:

```python
# (age > 18 AND status = 'active') OR role = 'admin'
await db.SELECT("*").FROM(users).WHERE(
    ((users.age > 18) & (users.status == "active")) | 
    (users.role == "admin")
).run()

# Multiple levels of nesting
await db.SELECT("*").FROM(users).WHERE(
    (
        ((users.age >= 18) & (users.age <= 65)) &
        (users.active == True)
    ) | (
        users.role.IN(['admin', 'moderator'])
    )
).run()
```

## Chaining WHERE Clauses

Multiple `.WHERE()` calls are combined with AND:

```python
# These are equivalent:
query1 = db.SELECT("*").FROM(users).WHERE(
    (users.age > 18) & (users.active == True)
)

query2 = db.SELECT("*").FROM(users).WHERE(
    users.age > 18
).WHERE(
    users.active == True
)

# Both generate: WHERE "users"."age" > $1 AND "users"."active" = $2
```

## JSON Filtering

For databases that support JSON operations (PostgreSQL, MySQL, SQLite):

```python
# Filter by JSON key
await db.SELECT("*").FROM(users).WHERE(
    users.meta["theme"] == "dark"
).run()
# PostgreSQL: WHERE users.meta->>'theme' = $1

# Nested JSON paths
await db.SELECT("*").FROM(users).WHERE(
    users.meta["preferences"]["notifications"] == "true"
).run()
```

## Condition Objects

Behind the scenes, SuperSQL uses several `Condition` classes:

- **`Condition`**: Basic comparisons (`==`, `>`, `<`, etc.)
- **`BooleanCondition`**: Logical operators (`&`, `|`, `~`)
- **`InCondition`**: IN and NOT IN operations
- **`BetweenCondition`**: BETWEEN operations

These objects:
- Implement `.compile(compiler)` to generate parameterized SQL
- Implement `__str__()` for debugging (shows literal values)
- Support nesting for complex boolean logic

```python
# You can inspect conditions:
condition = users.age > 18
print(str(condition))  # "users"."age" > 18 (literal for debugging)

# Compiled for actual query:
sql, params = condition.compile(compiler)
# sql: "users"."age" > $1
# params: [18]
```

## Security: SQL Injection Protection

SuperSQL automatically parameterizes all values:

```python
# ✅ SAFE - Automatically parameterized
user_input = "'; DROP TABLE users; --"  # Malicious input
await db.SELECT("*").FROM(users).WHERE(
    users.name == user_input
).run()
# SQL: WHERE "users"."name" = $1
# Parameters: ["'; DROP TABLE users; --"]
# The malicious input is treated as a literal string value

# ❌ UNSAFE - Using raw SQL strings
await db.SELECT("*").FROM(users).WHERE(
    f"name = '{user_input}'"  # DON'T DO THIS
).run()
```

!!! warning "Always Use Field Objects"
    For security, always use Field objects and operators for WHERE clauses. Avoid f-strings or string concatenation with user input.

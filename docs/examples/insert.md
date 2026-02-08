# INSERT Examples

Examples of inserting data with SuperSQL. All values are automatically parameterized for SQL injection protection.

## Basic INSERT

```python
from supersql import Query, Table

users = Table("users")
db = Query("postgres", database="mydb", user="user", password="pass")

# Single record
await db.INSERT_INTO(users, users.name, users.email, users.age).VALUES(
    "Alice", "alice@example.com", 30
).run()

# Generated SQL: INSERT INTO "users" ("name", "email", "age") VALUES ($1, $2, $3)
# Parameters: ["Alice", "alice@example.com", 30]
```

## INSERT Multiple Records

```python
# Multiple rows in one INSERT
await db.INSERT_INTO(users, users.name, users.email, users.age).VALUES(
    ("Alice", "alice@example.com", 30),
    ("Bob", "bob@example.com", 25),
    ("Charlie", "charlie@example.com", 35)
).run()

# Generated SQL:
# INSERT INTO "users" ("name", "email", "age") 
# VALUES ($1, $2, $3), ($4, $5, $6), ($7, $8, $9)
# Parameters: ["Alice", "alice@example.com", 30, "Bob", ...]
```

## INSERT with String Table Name

```python
# Using string table name
await db.INSERT_INTO("products", "name", "price", "category").VALUES(
    "Banana", 2.50, "Fruits"
).run()
```

## INSERT with RETURNING

Get the inserted data back (useful for auto-generated IDs):

```python
# Return inserted ID and timestamp
result = await db.INSERT_INTO(users, users.name, users.email).VALUES(
    "Dave", "dave@example.com"
).RETURNING(users.id, users.created_at).run()

print(result[0].id, result[0].created_at)
```

## INSERT with User Input (Safely Parameterized)

```python
# User input is automatically parameterized - safe from SQL injection
user_name = "John'; DROP TABLE users; --"  # Malicious input attempt
user_email = "john@example.com"
user_age = 28

await db.INSERT_INTO(users, users.name, users.email, users.age).VALUES(
    user_name, user_email, user_age
).run()

# The malicious input is safely parameterized as a literal string value
```

## INSERT from SELECT (Subquery)

```python
# Copy active users to an archive table
active_users = Table("active_users")
users_archive = Table("users_archive")

# Insert results of SELECT into another table
await db.INSERT_INTO(users_archive, "name", "email", "created_at").VALUES(
    db.SELECT(active_users.name, active_users.email, active_users.created_at).FROM(
        active_users
    ).WHERE(active_users.last_login < "2023-01-01")
).run()
```

## Batch INSERT with Loop

```python
# Insert many records from a list
new_users = [
    {"name": "Alice", "email": "alice@example.com", "age": 30},
    {"name": "Bob", "email": "bob@example.com", "age": 25},
    {"name": "Charlie", "email": "charlie@example.com", "age": 35},
]

# Convert to tuple format
values = [(u["name"], u["email"], u["age"]) for u in new_users]

await db.INSERT_INTO(users, users.name, users.email, users.age).VALUES(
    *values  # Unpack list of tuples
).run()
```

## INSERT with NULL Values

```python
# Explicitly insert NULL
await db.INSERT_INTO(users, users.name, users.email, users.phone).VALUES(
    "Eve", "eve@example.com", None  # None becomes NULL
).run()
```

## INSERT with Default Values

```python
# Skip columns with DEFAULT constraints
# Only insert name, let database set id, created_at, etc.
await db.INSERT_INTO(users, users.name).VALUES("Frank").run()
```

## Real-World Example: Order Entry

```python
orders = Table("orders")
order_items = Table("order_items")

# Insert order header
order_result = await db.INSERT_INTO(
    orders, orders.user_id, orders.total, orders.status
).VALUES(
    user_id, total_amount, "pending"
).RETURNING(orders.id).run()

order_id = order_result[0].id

# Insert order line items
items = [
    (order_id, product_id_1, quantity_1, price_1),
    (order_id, product_id_2, quantity_2, price_2),
]

await db.INSERT_INTO(
    order_items, 
    order_items.order_id, 
    order_items.product_id, 
    order_items.quantity, 
    order_items.price
).VALUES(*items).run()
```

## Tips

- **Always use parameterization**: Use Field objects and `VALUES()`, not f-strings
- **Batch inserts**: Insert multiple rows in one query for better performance
- **Use RETURNING**: Get auto-generated values without a separate SELECT
- **Handle user input carefully**: Even though values are parameterized, validate user input
- **Consider transactions**: Wrap related INSERTs in `BEGIN()`/`COMMIT()`

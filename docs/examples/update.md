# UPDATE Examples

Examples of updating data with SuperSQL. All values are automatically parameterized for SQL injection protection.

## Basic UPDATE

```python
from supersql import Query, Table

users = Table("users")
db = Query("postgres", database="mydb", user="user", password="pass")

# Update single column
await db.UPDATE(users).SET(
    users.name == "John Smith"
).WHERE(users.id == 1).run()

# Generated SQL: UPDATE "users" SET "name" = $1 WHERE "users"."id" = $2
# Parameters: ["John Smith", 1]
```

## UPDATE Multiple Columns

```python
# Update several columns at once
await db.UPDATE(users).SET(
    users.name == "John Smith",
    users.email == "john.smith@example.com",
    users.age == 31
).WHERE(users.id == 1).run()

# Generated SQL:
# UPDATE "users" SET "name" = $1, "email" = $2, "age" = $3 
# WHERE "users"."id" = $4
# Parameters: ["John Smith", "john.smith@example.com", 31, 1]
```

## UPDATE with User Input (Safely Parameterized)

```python
# User input is automatically parameterized - safe from SQL injection
user_id = 42
new_status = "active'; DROP TABLE users; --"  # Malicious attempt

await db.UPDATE(users).SET(
    users.status == new_status
).WHERE(users.id == user_id).run()

# The malicious input is safely parameterized as a literal string value
# Generated SQL: UPDATE "users" SET "status" = $1 WHERE "users"."id" = $2
# Parameters: ["active'; DROP TABLE users; --", 42]
```

## UPDATE with Complex WHERE

```python
# Update users matching multiple conditions
await db.UPDATE(users).SET(
    users.status == "verified"
).WHERE(
    (users.email_confirmed == True) &
    (users.age >= 18) &
    (users.created_at < "2024-01-01")
).run()
```

## UPDATE Without WHERE (Update All)

```python
# Update all rows - BE CAREFUL!
await db.UPDATE(users).SET(
    users.last_checked == "2024-01-15"
).run()

# Updates EVERY row in the table
```

## Conditional UPDATE

```python
# Update only if condition is met
min_balance = 100

await db.UPDATE(users).SET(
    users.account_type == "premium"
).WHERE(
    users.balance >= min_balance
).run()
```

## UPDATE with Increment/Decrement

```python
# Increment a counter (using raw SQL expression for now)
await db.UPDATE(users).SET(
    "login_count = login_count + 1"
).WHERE(users.id == user_id).run()

# Decrement balance
await db.UPDATE(users).SET(
    "balance = balance - 50"
).WHERE(users.id == user_id).run()
```

## UPDATE with RETURNING

```python
# Get updated values back
result = await db.UPDATE(users).SET(
    users.status == "active",
    users.last_login == "2024-01-15"
).WHERE(users.id == 1).RETURNING(
    users.id, users.status, users.last_login
).run()

if result:
    print(f"Updated user {result[0].id}: {result[0].status}")
```

## Bulk UPDATE from List

```python
# Update multiple users with a loop (less efficient)
user_updates = [
    (1, "Alice Smith"),
    (2, "Bob Johnson"),
    (3, "Charlie Brown"),
]

for user_id, new_name in user_updates:
    await db.UPDATE(users).SET(
        users.name == new_name
    ).WHERE(users.id == user_id).run()
```

## UPDATE with Subquery

```python
# Update based on aggregated data from another table
orders = Table("orders")

# Set user tier based on total purchase amount
await db.UPDATE(users).SET(
    users.tier == "gold"
).WHERE(
    f"""users.id IN (
        SELECT user_id FROM orders 
        GROUP BY user_id 
        HAVING SUM(total) > 1000
    )"""
).run()
```

## UPDATE with JOIN (PostgreSQL)

```python
# Update users based on related table data
posts = Table("posts")

# PostgreSQL syntax for UPDATE with JOIN
await db.UPDATE(users).SET(
    users.post_count == "subquery.count"
).FROM(
    """(
        SELECT user_id, COUNT(*) as count 
        FROM posts 
        GROUP BY user_id
    ) as subquery"""
).WHERE("users.id = subquery.user_id").run()
```

## Real-World Example: User Profile Update

```python
# Update user profile with validation
def update_user_profile(user_id, profile_data):
    # profile_data from user input (form submission)
    name = profile_data.get("name")
    email = profile_data.get("email")
    bio = profile_data.get("bio")
    
    # All values are safely parameterized
    return await db.UPDATE(users).SET(
        users.name == name,
        users.email == email,
        users.bio == bio,
        users.updated_at == "NOW()"
    ).WHERE(users.id == user_id).RETURNING(
        users.id, users.name, users.email
    ).run()

# Usage
updated_user = await update_user_profile(42, {
    "name": "John Doe",
    "email": "john@example.com",
    "bio": "Software developer"
})
```

## Real-World Example: Order Status Update

```python
orders = Table("orders")

# Update order status with timestamp
async def update_order_status(order_id, new_status):
    return await db.UPDATE(orders).SET(
        orders.status == new_status,
        orders.status_changed_at == "NOW()"
    ).WHERE(
        (orders.id == order_id) &
        (orders.status != "cancelled")  # Don't update cancelled orders
    ).RETURNING(orders.id, orders.status).run()

# Usage
result = await update_order_status(123, "shipped")
if result:
    print(f"Order {result[0].id} status: {result[0].status}")
else:
    print("Order not found or was cancelled")
```

## Tips

- **Always use WHERE**: Avoid accidental update-all operations
- **Use transactions**: Wrap critical updates in `BEGIN()`/`COMMIT()`
- **Use RETURNING**: Verify updates succeeded
- **Parameterization is automatic**: User input is safely handled
- **Validate before updating**: Check business logic before database changes
- **Consider concurrency**: Use row-level locking for critical updates
- **Audit changes**: Log important updates for compliance/debugging
# Examples

This section contains common patterns and examples for using SuperSQL.

# Examples

This section contains common patterns and examples for using SuperSQL.

## 1. Defining Tables

```python
from supersql import Table

# Define tables dynamically
users = Table("users")
posts = Table("posts")
```

## 2. Basic CRUD

### Create (INSERT)
```python
# Insert one
await query.INSERT(users).VALUES(email="alice@example.com").run()

# Insert many
data = [
    {"email": "bob@example.com", "is_active": True},
    {"email": "charlie@example.com", "is_active": False},
]
await query.INSERT(users).VALUES(data).run()
```

### Read (SELECT)
```python
# Select all active users
users_list = await query.SELECT(users).FROM(users).WHERE(users.is_active == True).run()

# Select specific columns
emails = await query.SELECT(users.email).FROM(users).LIMIT(5).run()
```

### Update (UPDATE)
```python
# Activate a user
await query.UPDATE(users).SET(users.is_active == True).WHERE(users.email == "charlie@example.com").run()
```

### Delete (DELETE)
```python
# Delete inactive users
await query.DELETE(users).WHERE(users.is_active == False).run()
```

## 3. Advanced Querying

### Joins with Aggregation
Count posts per user.

```python
await query.SELECT(
    users.email, 
    query.COUNT(posts.id).AS("post_count")
).FROM(
    users
).LEFT_JOIN(
    posts, ON=(users.id == posts.user_id)
).GROUP_BY(
    users.email
).run()
```

### Common Table Expressions (CTEs)
Find users who have published more than 5 posts.

```python
# 1. CTE: Calculate post counts
post_counts = query.SELECT(
    posts.user_id, 
    query.COUNT("*").AS("cnt")
).FROM(
    posts
).WHERE(
    posts.published == True
).GROUP_BY(
    posts.user_id
)

# 2. Main Query: Join CTE
await query.WITH(
    "stats", post_counts
).SELECT(
    users.email
).FROM(
    users
).JOIN(
    "stats", ON=(users.id == query.field("stats.user_id"))
).WHERE(
    query.field("stats.cnt") > 5
).run()
```

### JSON Operations
Querying a generic `meta` JSON column.

```python
logs = Table("logs")

# Find logs where data->'level' is 'error'
errors = await query.SELECT(logs).FROM(logs).WHERE(logs.data["level"] == "error").run()
```

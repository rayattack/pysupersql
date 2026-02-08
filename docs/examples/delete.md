# DELETE Examples

Examples of deleting data with SuperSQL. All WHERE clause values are automatically parameterized for SQL injection protection.

## Basic DELETE

```python
from supersql import Query, Table

users = Table("users")
db = Query("postgres", database="mydb", user="user", password="pass")

# Delete a single record
await db.DELETE_FROM(users).WHERE(users.id == 1).run()

# Generated SQL: DELETE FROM "users" WHERE "users"."id" = $1
# Parameters: [1]
```

## DELETE with Multiple Conditions

```python
# Delete records matching multiple criteria
await db.DELETE_FROM(users).WHERE(
    (users.status == "inactive") &
    (users.last_login < "2023-01-01") &
    (users.email_confirmed == False)
).run()

# Generated SQL:
# DELETE FROM "users" WHERE 
# ("users"."status" = $1) AND 
# ("users"."last_login" < $2) AND 
# ("users"."email_confirmed" = $3)
# Parameters: ["inactive", "2023-01-01", False]
```

## DELETE with User Input (Safely Parameterized)

```python
# User input is automatically parameterized - safe from SQL injection
user_id = 42  # From user request

await db.DELETE_FROM(users).WHERE(users.id == user_id).run()

# Even malicious input is safe:
malicious_id = "1; DROP TABLE users; --"
await db.DELETE_FROM(users).WHERE(users.id == malicious_id).run()
# The malicious string is treated as a literal value (won't match any id)
```

## DELETE All Records (Dangerous!)

```python
# Delete ALL records from table - USE WITH EXTREME CAUTION
await db.DELETE_FROM(users).run()

# No WHERE clause = deletes everything!
# Consider using TRUNCATE for better performance:
# await db.TRUNCATE(users).run()
```

## DELETE with IN

```python
# Delete multiple records by ID
ids_to_delete = [1, 5, 10, 15]

await db.DELETE_FROM(users).WHERE(
    users.id.IN(ids_to_delete)
).run()

# Generated SQL: DELETE FROM "users" WHERE "users"."id" IN ($1, $2, $3, $4)
# Parameters: [1, 5, 10, 15]
```

## DELETE with RETURNING

```python
# Get deleted records back (useful for audit logs)
result = await db.DELETE_FROM(users).WHERE(
    users.status == "banned"
).RETURNING(users.id, users.name, users.email).run()

# Log deleted users
for user in result:
    print(f"Deleted: {user.id} - {user.name} ({user.email})")
```

## Soft DELETE (Mark as Deleted)

```python
# Don't actually delete - just mark as deleted
await db.UPDATE(users).SET(
    users.deleted_at == "NOW()",
    users.status == "deleted"
).WHERE(users.id == user_id).run()

# Later, filter out soft-deleted records in SELECT queries
active_users = await db.SELECT("*").FROM(users).WHERE(
    users.deleted_at.IS_NULL()
).run()
```

## DELETE with Subquery

```python
# Delete users who haven't made any orders
orders = Table("orders")

await db.DELETE_FROM(users).WHERE(
    f"""users.id NOT IN (
        SELECT DISTINCT user_id FROM orders
    )"""
).run()
```

## DELETE with JOIN (PostgreSQL)

```python
# Delete users based on related table
posts = Table("posts")

# PostgreSQL: DELETE with USING
await db.DELETE_FROM(users).run(
    raw_sql="""
    DELETE FROM users
    USING posts
    WHERE users.id = posts.user_id
    AND posts.spam_count > 10
    """
)
```

## Cascade DELETE

```python
# Database-level cascading should be configured in schema
# But you can manually delete related records:

user_id_to_delete = 42

# Delete user's posts first
await db.DELETE_FROM(posts).WHERE(posts.user_id == user_id_to_delete).run()

# Then delete user
await db.DELETE_FROM(users).WHERE(users.id == user_id_to_delete).run()
```

## DELETE with Transaction

```python
# Wrap deletes in transaction for safety
await db.BEGIN().run()

try:
    # Delete related records
    await db.DELETE_FROM(posts).WHERE(posts.user_id == user_id).run()
    await db.DELETE_FROM(comments).WHERE(comments.user_id == user_id).run()
    await db.DELETE_FROM(users).WHERE(users.id == user_id).run()
    
    await db.COMMIT().run()
except Exception as e:
    await db.ROLLBACK().run()
    print(f"Delete failed: {e}")
```

## Real-World Example: Cleanup Old Records

```python
# Delete old inactive accounts
async def cleanup_inactive_users(days_inactive=365):
    cutoff_date = f"NOW() - INTERVAL '{days_inactive} days'"
    
    # Get count first
    count_query = await db.SELECT("COUNT(*) as count").FROM(users).WHERE(
        (users.last_login < cutoff_date) &
        (users.status == "inactive")
    ).run()
    
    count = count_query[0].count if count_query else 0
    
    if count == 0:
        return 0
    
    # Delete and return deleted records for logging
    deleted = await db.DELETE_FROM(users).WHERE(
        (users.last_login < cutoff_date) &
        (users.status == "inactive")
    ).RETURNING(users.id, users.email, users.last_login).run()
    
    return deleted

# Usage
deleted_users = await cleanup_inactive_users(365)
print(f"Cleaned up {len(deleted_users)} inactive users")
```

## Real-World Example: Delete with Confirmation

```python
# Safe delete function with confirmation
async def safe_delete_user(user_id, confirmation_code):
    # First, verify confirmation code
    user = await db.SELECT(users.id, users.email).FROM(users).WHERE(
        (users.id == user_id) &
        (users.deletion_code == confirmation_code)
    ).run()
    
    if not user:
        raise ValueError("Invalid user ID or confirmation code")
    
    # Archive user data before deleting
    archive = Table("deleted_users_archive")
    user_data = await db.SELECT("*").FROM(users).WHERE(
        users.id == user_id
    ).run()
    
    # Insert into archive
    await db.INSERT_INTO(archive, "user_id", "email", "deleted_at").VALUES(
        user_data[0].id, user_data[0].email, "NOW()"
    ).run()
    
    # Delete user and get confirmation
    result = await db.DELETE_FROM(users).WHERE(
        users.id == user_id
    ).RETURNING(users.id, users.email).run()
    
    return result[0] if result else None

# Usage
deleted = await safe_delete_user(42, "ABC123")
if deleted:
    print(f"Deleted user {deleted.email}")
```

## Tips

- **Always use WHERE**: Avoid accidental delete-all operations
- **Use transactions**: Wrap related deletes in `BEGIN()`/`COMMIT()`
- **Consider soft deletes**: Mark as deleted instead of removing
- **Archive important data**: Copy to archive table before deleting
- **Use RETURNING**: Log what was deleted for audit purposes
- **Test in development**: Test DELETE queries with SELECT first
- **Backup before bulk deletes**: Always have backups before large delete operations
- **Foreign key constraints**: Ensure proper CASCADE/RESTRICT settings
- **Parameterization is automatic**: User input is safely handled
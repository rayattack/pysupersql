# Joins

SuperSQL provides a Pythonic interface for all standard SQL join types with automatic identifier quoting and parameterization.

## Basic Joins

The `.JOIN()` method defaults to an **INNER JOIN**. Table and column identifiers are automatically quoted.

```python
from supersql import Query, Table

users = Table("users")
posts = Table("posts")
db = Query("postgres", database="mydb")

# SELECT * FROM "users" INNER JOIN "posts" ON "users"."id" = "posts"."user_id"
await db.SELECT("*").FROM(users).JOIN(
    posts, on=f"{users.id} = {posts.user_id}"
).run()

# Or use Condition objects for type safety
await db.SELECT("*").FROM(users).JOIN(
    posts, on=(users.id == posts.user_id)
).run()
```

## Join Types

SuperSQL supports all standard SQL join types:

| Method | SQL Equivalent | Description |
|--------|----------------|-------------|
| `.JOIN(table, on=...)` app `INNER JOIN` | Returns records with matching values in both tables. |
| `.LEFT_JOIN(table, on=...)` | `LEFT JOIN` | Returns all records from left table, and matched from right. |
| `.RIGHT_JOIN(table, on=...)` | `RIGHT JOIN` | Returns all records from right table, and matched from left. |
| `.FULL_JOIN(table, on=...)` | `FULL OUTER JOIN` | Returns all records when there is a match in either table. |
| `.CROSS_JOIN(table)` | `CROSS JOIN` | Returns the Cartesian product of both tables (no ON clause). |

### Examples

```python
users = Table("users")
posts = Table("posts")
comments = Table("comments")

# INNER JOIN
await db.SELECT(users.name, posts.title).FROM(users).JOIN(
    posts, on=(users.id == posts.user_id)
).run()

# LEFT JOIN - Get all users, even those without posts
await db.SELECT(users.name, posts.title).FROM(users).LEFT_JOIN(
    posts, on=(users.id == posts.user_id)
).run()

# RIGHT JOIN
await db.SELECT(users.name, posts.title).FROM(users).RIGHT_JOIN(
    posts, on=(users.id == posts.user_id)
).run()

# FULL OUTER JOIN
await db.SELECT(users.name, posts.title).FROM(users).FULL_JOIN(
    posts, on=(users.id == posts.user_id)
).run()

# CROSS JOIN (no ON clause)
sizes = Table("sizes")
colors = Table("colors")
await db.SELECT("*").FROM(sizes).CROSS_JOIN(colors).run()
```

## Multiple Joins

Chain multiple `.JOIN()` calls for complex queries:

```python
# Join three tables
await db.SELECT(
    users.name,
    posts.title,
    comments.content
).FROM(users).JOIN(
    posts, on=(users.id == posts.user_id)
).JOIN(
    comments, on=(posts.id == comments.post_id)
).run()
```

## Complex ON Clauses

Use logical operators (`&`, `|`, `~`) in your `ON` clause:

```python
# JOIN with multiple conditions
await db.SELECT(users.name, posts.title).FROM(users).JOIN(
    posts, 
    on=(
        (users.id == posts.user_id) & 
        (posts.published == True) &
        (posts.deleted_at.IS_NULL())
    )
).run()

# Generated SQL:
# INNER JOIN "posts" ON (
#   ("users"."id" = "posts"."user_id") AND 
#   ("posts"."published" = $1) AND
#   ("posts"."deleted_at" IS NULL)
# )
# Parameters: [True]
```

## Self Joins

To join a table to itself, use table aliases with `.AS()`:

```python
employees = Table("employees")
managers = employees.AS("mgr")  # Create alias

# Find employees and their managers
await db.SELECT(
    employees.name.AS("employee_name"),
    managers.name.AS("manager_name")
).FROM(employees).LEFT_JOIN(
    managers, on=(employees.manager_id == managers.id)
).run()

# Generated SQL:
# SELECT 
#   "employees"."name" AS employee_name,
#   "mgr"."name" AS manager_name
# FROM "employees"
# LEFT JOIN "employees" AS "mgr" ON "employees"."manager_id" = "mgr"."id"
```

## Table Aliases in Joins

Use aliases to shorten queries and avoid ambiguity:

```python
u = Table("users").AS("u")
p = Table("posts").AS("p")
c = Table("comments").AS("c")

await db.SELECT(
    u.name,
    p.title,
    c.content
).FROM(u).JOIN(
    p, on=(u.id == p.user_id)
).JOIN(
    c, on=(p.id == c.post_id)
).run()

# SELECT "u"."name", "p"."title", "c"."content"
# FROM "users" AS "u"
# INNER JOIN "posts" AS "p" ON "u"."id" = "p"."user_id"
# INNER JOIN "comments" AS "c" ON "p"."id" = "c"."post_id"
```

## Schema-Qualified Tables

Join tables from different schemas:

```python
public_users = Table("users", schema="public")
analytics_events = Table("events", schema="analytics")

await db.SELECT(
    public_users.id,
    analytics_events.event_name
).FROM(public_users).JOIN(
    analytics_events, on=(public_users.id == analytics_events.user_id)
).run()

# FROM "public"."users"
# INNER JOIN "analytics"."events" ON ...
```

## Joining with Subqueries

You can join with subqueries (CTEs):

```python
# Create a CTE for recent posts
recent_posts = db.SELECT(posts.id, posts.user_id, posts.title).FROM(posts).WHERE(
    posts.created_at > "2024-01-01"
)

# Join users with the CTE
await db.WITH("recent_posts", recent_posts).SELECT(
    users.name,
    "recent_posts.title"
).FROM(users).JOIN(
    "recent_posts", on="users.id = recent_posts.user_id"
).run()
```

## Join Performance Tips

1. **Use indexes**: Ensure columns in ON clauses are indexed
2. **Filter early**: Apply WHERE clauses before joins when possible
3. **Select specific columns**: Avoid `SELECT *` in joins
4. **Consider LEFT JOIN carefully**: They can be slower than INNER JOIN

```python
# Good: Filter before join
filtered_users = db.SELECT(users.id, users.name).FROM(users).WHERE(
    users.active == True
)

await db.WITH("active_users", filtered_users).SELECT(
    "active_users.name",
    posts.title
).FROM("active_users").JOIN(
    posts, on="active_users.id = posts.user_id"
).run()
```

## Identifier Quoting

SuperSQL automatically quotes all identifiers to handle:
- Reserved SQL keywords as table/column names
- Case-sensitive identifiers
- Special characters in names

```python
# These are all properly quoted:
order = Table("order")  # "order" is a SQL keyword
await db.SELECT(order.id).FROM(order).run()
# SELECT "order"."id" FROM "order"

user_info = Table("user-info")  # Hyphen in name
await db.SELECT(user_info.id).FROM(user_info).run()
# SELECT "user-info"."id" FROM "user-info"
```

## Parameterization in Joins

Values in ON clauses are automatically parameterized:

```python
# Constants in ON clause are parameterized
await db.SELECT("*").FROM(users).JOIN(
    posts, on=((users.id == posts.user_id) & (posts.status == "published"))
).run()

# Generated SQL:
# ... ON ("users"."id" = "posts"."user_id") AND ("posts"."status" = $1)
# Parameters: ["published"]
```

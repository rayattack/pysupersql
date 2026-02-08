# Common Table Expressions (CTEs)

Common Table Expressions (CTEs) allow you to define temporary named result sets that can be referenced within your main query. SuperSQL supports CTEs through the `.WITH()` method.

## Basic CTE

Create a CTE using `.WITH(name, subquery)`:

```python
from supersql import Query, Table

users = Table("users")
orders = Table("orders")
db = Query("postgres", database="mydb")

# Define a CTE for active users
active_users_query = db.SELECT(
    users.id, users.name, users.email
).FROM(users).WHERE(
    users.active == True
)

# Use the CTE in main query
result = await db.WITH("active_users", active_users_query).SELECT(
    "*"
).FROM("active_users").run()
```

**Generated SQL:**
```sql
WITH active_users AS (
  SELECT "users"."id", "users"."name", "users"."email" 
  FROM "users" 
  WHERE "users"."active" = $1
)
SELECT * FROM "active_users"
```

## Multiple CTEs

Chain `.WITH()` calls to define multiple CTEs:

```python
# Define first CTE: high-value orders
high_value_orders = db.SELECT(
    orders.id, orders.user_id, orders.total
).FROM(orders).WHERE(
    orders.total > 1000
)

# Define second CTE: active users
active_users = db.SELECT(
    users.id, users.name, users.email
).FROM(users).WHERE(
    users.active == True
)

# Use both CTEs in main query
result = await db.WITH("high_value", high_value_orders).WITH(
    "active", active_users
).SELECT(
    "active.name",
    "high_value.total"
).FROM("active").JOIN(
    "high_value", on="active.id = high_value.user_id"
).run()
```

**Generated SQL:**
```sql
WITH high_value AS (
  SELECT "orders"."id", "orders"."user_id", "orders"."total"
  FROM "orders"
  WHERE "orders"."total" > $1
),
active AS (
  SELECT "users"."id", "users"."name", "users"."email"
  FROM "users"
  WHERE "users"."active" = $2
)
SELECT active.name, high_value.total
FROM "active"
INNER JOIN "high_value" ON active.id = high_value.user_id
```

## CTE with Aggregations

Use CTEs to simplify complex aggregation queries:

```python
products = Table("products")
sales = Table("sales")

# CTE: Calculate total sales per product
sales_summary = db.SELECT(
    sales.product_id,
    "SUM(sales.quantity) as total_quantity",
    "SUM(sales.amount) as total_revenue"
).FROM(sales).GROUP_BY(sales.product_id)

# Main query: Join with products to get details
result = await db.WITH("sales_summary", sales_summary).SELECT(
    products.name,
    "sales_summary.total_quantity",
    "sales_summary.total_revenue"
).FROM(products).JOIN(
    "sales_summary", on="products.id = sales_summary.product_id"
).run()
```

## CTE for Data Transformation

CTEs are useful for multi-step data transformations:

```python
raw_data = Table("raw_events")

# Step 1: Filter and clean recent events
recent_events = db.SELECT(
    raw_data.user_id,
    raw_data.event_type,
    raw_data.created_at
).FROM(raw_data).WHERE(
    (raw_data.created_at > "2024-01-01") &
    (raw_data.event_type.IN(["login", "purchase", "signup"]))
)

# Step 2: Count events per user
user_activity = db.SELECT(
    "recent_events.user_id",
    "COUNT(*) as event_count"
).FROM("recent_events").GROUP_BY("recent_events.user_id")

# Step 3: Find top active users
result = await db.WITH("recent_events", recent_events).WITH(
    "user_activity", user_activity
).SELECT(
    users.name,
    "user_activity.event_count"
).FROM(users).JOIN(
    "user_activity", on="users.id = user_activity.user_id"
).WHERE("user_activity.event_count > 10").run()
```

## CTE with String Subqueries

You can also pass raw SQL strings as CTEs:

```python
# Define CTE as raw SQL
older_users_sql = "SELECT id, name FROM users WHERE age > 50"

# Use in main query
result = await db.WITH("older_users", older_users_sql).DELETE_FROM(
    "older_users"
).run()
```

## Nested CTEs

CTEs can reference other CTEs defined earlier in the chain:

```python
# CTE 1: Base data
base_data = db.SELECT(
    orders.id,
    orders.user_id,
    orders.total,
    orders.created_at
).FROM(orders)

# CTE 2: Uses CTE 1
monthly_totals = db.SELECT(
    "base.user_id",
    "DATE_TRUNC('month', base.created_at) as month",
    "SUM(base.total) as monthly_total"
).FROM("base").GROUP_BY("base.user_id", "month")

# Main query uses CTE 2
result = await db.WITH("base", base_data).WITH(
    "monthly_totals", monthly_totals
).SELECT(
    users.name,
    "monthly_totals.month",
    "monthly_totals.monthly_total"
).FROM(users).JOIN(
    "monthly_totals", on="users.id = monthly_totals.user_id"
).run()
```

## Real-World Example: User Purchase Analysis

```python
users = Table("users")
orders = Table("orders")
order_items = Table("order_items")

# CTE 1: Calculate total spending per user
user_spending = db.SELECT(
    orders.user_id,
    "SUM(order_items.price * order_items.quantity) as total_spent",
    "COUNT(DISTINCT orders.id) as order_count"
).FROM(orders).JOIN(
    order_items, on=(orders.id == order_items.order_id)
).GROUP_BY(orders.user_id)

# CTE 2: Calculate average order value
avg_values = db.SELECT(
    "user_spending.user_id",
    "(user_spending.total_spent / user_spending.order_count) as avg_order_value"
).FROM("user_spending")

# Main query: Find high-value customers
result = await db.WITH("user_spending", user_spending).WITH(
    "avg_values", avg_values
).SELECT(
    users.name,
    users.email,
    "avg_values.avg_order_value",
    "user_spending.order_count"
).FROM(users).JOIN(
    "user_spending", on="users.id = user_spending.user_id"
).JOIN(
    "avg_values", on="users.id = avg_values.user_id"
).WHERE("avg_values.avg_order_value > 100").ORDER_BY(
    "-avg_order_value"
).LIMIT(10).run()
```

**Generated SQL:**
```sql
WITH user_spending AS (
  SELECT 
    "orders"."user_id",
    SUM(order_items.price * order_items.quantity) as total_spent,
    COUNT(DISTINCT orders.id) as order_count
  FROM "orders"
  INNER JOIN "order_items" ON "orders"."id" = "order_items"."order_id"
  GROUP BY "orders"."user_id"
),
avg_values AS (
  SELECT 
    user_spending.user_id,
    (user_spending.total_spent / user_spending.order_count) as avg_order_value
  FROM "user_spending"
)
SELECT 
  "users"."name",
  "users"."email",
  avg_values.avg_order_value,
  user_spending.order_count
FROM "users"
INNER JOIN "user_spending" ON users.id = user_spending.user_id
INNER JOIN "avg_values" ON users.id = avg_values.user_id
WHERE avg_values.avg_order_value > 100
ORDER BY avg_order_value DESC
LIMIT 10
```

## Benefits of CTEs

1. **Readability**: Break complex queries into logical steps
2. **Reusability**: Reference the same subquery multiple times
3. **Maintainability**: Easier to debug and modify
4. **Performance**: Database can optimize CTE execution
5. **Organization**: Group related transformations together

## When to Use CTEs

- **Complex aggregations**: Multiple levels of grouping
- **Data transformation pipelines**: Sequential cleaning/filtering steps
- **Recursive queries**: Hierarchical data (see `with-recursive.md`)
- **Code organization**: Breaking down monolithic queries
- **Temporary intermediate results**: Results needed multiple times

## Tips

- Name CTEs descriptively (`active_users`, `monthly_totals`)
- Order CTEs logically (dependencies first)
- Use CTEs for readability even when not strictly necessary
- Consider indexes on columns used in CTE WHERE clauses
- For very large datasets, materialized views might be better than CTEs
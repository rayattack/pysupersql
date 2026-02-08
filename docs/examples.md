# Supersql Examples

Supersql provides a fluid, pythonic syntax for building complex SQL queries. The new AST-based engine allows for robust query construction, including support for Common Table Expressions (CTEs) and complex joins.

## E-Commerce Power Examples

Here are some examples demonstrating how to use Supersql in an e-commerce context, dealing with Products, Carts, and Purchases.

### 1. Simple Product Fetching

Retrieve active products with a price greater than 100, ordered by price.

```python
from supersql import Query, Table, Integer, String, Boolean, Float

class Products(Table):
    id = Integer()
    name = String()
    price = Float()
    active = Boolean()

q = Query('postgres://user:pass@localhost:5432/db')
p = Products()

query = q.SELECT(p.name, p.price).FROM(p) \
         .WHERE(p.active == True) \
         .WHERE(p.price > 100) \
         .ORDER_BY('-price') \
         .LIMIT(10)

# SQL: SELECT products.name, products.price FROM products WHERE products.active = true AND products.price > 100 ORDER BY price DESC LIMIT 10
results = query.execute()
```

### 2. Shopping Cart Analysis with Joins

Find all items in a specific user's cart, including product details.

```python
class Carts(Table):
    id = Integer()
    user_id = Integer()

class CartItems(Table):
    id = Integer()
    cart_id = Integer()
    product_id = Integer()
    quantity = Integer()

u_id = 123
c = Carts()
ci = CartItems()
p = Products()

# Cartesian join power with explicit ON
query = q.SELECT(p.name, ci.quantity, p.price) \
         .FROM(c) \
         .JOIN(ci, on=c.id == ci.cart_id) \
         .JOIN(p, on=ci.product_id == p.id) \
         .WHERE(c.user_id == u_id)

# Execute
data = query.execute()
```

### 3. Advanced Analytics Using CTEs (Common Table Expressions)

Use CTEs to calculate the total purchases per user, then select high-value customers.

```python
class Purchases(Table):
    id = Integer()
    user_id = Integer()
    total_amount = Float()
    created_at = String() # Simplified date

pur = Purchases()

# Define the CTE: Aggregated sales per user
user_totals = q.SELECT(pur.user_id, 'SUM(total_amount) as lifetime_value') \
               .FROM(pur) \
               .GROUP_BY(pur.user_id)

# Use the CTE in the main query
# WITH user_stats AS (SELECT ...) SELECT * FROM user_stats WHERE lifetime_value > 1000
query = q.WITH('user_stats', user_totals) \
         .SELECT('*') \
         .FROM('user_stats') \
         .WHERE('lifetime_value > 1000')

# SQL Generation (Generalized):
# WITH user_stats AS (SELECT purchases.user_id, SUM(total_amount) as lifetime_value FROM purchases GROUP BY purchases.user_id)
# SELECT * FROM user_stats WHERE lifetime_value > 1000

# Execute
vip_users = query.execute()
```

### 4. Recursive Queries (Hierarchical Categories)

(Note: Recursive CTE syntax support is consistent with standard CTEs)

```python
class Categories(Table):
    id = Integer()
    parent_id = Integer()
    name = String()

cat = Categories()

# Base case
base = q.SELECT(cat.id, cat.name, cat.parent_id).FROM(cat).WHERE(cat.parent_id == 0) # Root categories

# Recursive step (Conceptual example, assuming recursive union support via raw SQL or future expansion)
# Currently, you can structure multiple CTEs for layered analysis.

q.WITH('roots', base).SELECT('*').FROM('roots').execute()
```

## Parameterization & Security

Supersql automatically parameterizes values in `WHERE` clauses to prevent SQL injection.

```python
# Values are safely parameterized
q.SELECT(p).FROM(p).WHERE(p.name == "O'Reilly's Books").execute()
# Resulting SQL uses placeholders: ... WHERE products.name = $1
```

# Table Definition

SuperSQL uses a dynamic `Table` object to represent database structure. There is no need to define Python classes or duplicate your schema.

## Creating a Table

Simply instantiate the `Table` class with your table string name.

```python
from supersql import Table

users = Table("users")
```

## Using Columns

You can access any column on the table using dot notation. These columns are created dynamically when you access them.

```python
# Returns a Field object representing "users.email"
users.email 

# Returns a Field object representing "users.created_at"
users.created_at
```

## Schemas & Aliases

### Database Schemas
If your table is in a specific database schema (like `public` or `analytics`), pass it as the second argument.

```python
# analytics.events
events = Table("events", schema="analytics")
```

### Aliases
You can alias tables for clearer queries or self-joins.

```python
# items AS i
items = Table("items").AS("i")

# SELECT i.name FROM items AS i
query.SELECT(items.name).FROM(items)
```

## Self Joins

You can create multiple instances of the same table with different aliases.

```python
Employee = Table("employees")
Manager = Employee.AS("mgr")

query.SELECT(
    Employee.name, Manager.name
).FROM(
    Employee
).LEFT_JOIN(
    Manager, ON=(Employee.manager_id == Manager.id)
)
```

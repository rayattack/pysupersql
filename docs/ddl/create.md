# DDL Operations (CREATE)

SuperSQL isn't just for querying; it can also manage your database schema.

## Creating Tables

You can generate `CREATE TABLE` statements directly from your `Table` classes.

```python
from supersql import Table, String, Integer, Serial

class User(Table):
    id = Serial(pk=True)
    username = String(unique=True)
    age = Integer()

# Generate SQL
query.CREATE_TABLE(User).run()
```

This generates SQL similar to:
```sql
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    age INTEGER
);
```

## Creating Databases

```python
query.CREATE_DATABASE("mydb").run()
```

## Creating Indexes

*Note: Explicit index creation support via Python API is currently in development. Use raw SQL for complex indexes.*

```python
query.raw("CREATE INDEX idx_user_name ON user (username)").run()
```

## Dropping Tables

```python
# DROP TABLE user
query.DROP_TABLE(User).run()

# DROP TABLE IF EXISTS user
query.DROP_TABLE(User, if_exists=True).run()
```

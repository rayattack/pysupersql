# Made For Humans
Supersql is a `very thin wrapper` on top of SQL that enables you write SQL code in python.


## Why?
Let's be honest, creating **SQL** templates with string interpolation is really painful.

Almost all ORMs write the query for you behind the scenes and as such you can only use the interface
they provide which most times is not enough for complex query needs.

SqlAlchemy is almost different, and SuperSQL is not trying to be a replacement, it just takes you
closer to SQL than any other library (at least at the time it was created), this allows you to:

- Take the full power of python to SQL
- Create advanced queries i.e. `Recursive Queries, Joins, Functions, Triggers, DDL` etc.
- Use different SQL dialects `(Athena, Postgres, MySQL, MariaDB, Oracle, MSSQL, SQLite etc.)`


## Query Quickstart

There are 4 ways to query your data in SuperSQL

- Manually create a Supersql _**Table**_ schema
- Automatically reflect a table schema object from the database
- Use _`dict`_ and _`list`_ with **variables**
- Identifier Interpolation


&nbsp;
#### Manually Create Table Schema
```py
from supersql import Table
from supersql import (
    Date,
    Integer,
    String,
    UUID,
)


class Employee(Table):
    identifier = UUID(postgres='uuid_version1')
    first_name = String(required=True)
    last_name = String(25)
    email = String(25, required=True, unique=True)
    age = Integer()
    created_on = Date()


emp = Employee()


results = query.SELECT(
    emp.first_name, emp.last_name, emp.email
).FROM(
    emp
).WHERE(
    emp.email == 'someone@example.com'
).execute()

```
&nbsp;
#### Auto-Reflect Table Schema
```py
from supersql import Query
from mycodebase import config_dict


query = Query(...)  # connection parameters as required


tables = query.database("dbname").tables()
emp = tables.get("employees")


results = query.SELECT(
    emp.first_name, emp.last_name, emp.email
).FROM(
    emp
).WHERE(
    emp.email == 'someone@example.com'
).execute()  # same as run()

```

&nbsp;

#### Use Dict &amp; Lists with Variables
```py

from supersql import Query

query = Query(...)  # connection parameters as required

def example(table, *args, **kwargs)
    alt_results = query.SELECT(*args).FROM(table).WHERE(**kwargs).run()
```

&nbsp;

#### Identifier Interpolation

Identifier interpolation allows you to use strings and constant values in place of column names and
other identifiers.

```py

from supersql import Query

query = Query()

# Notice that we 
results = query.SELECT(
    "first_name", "last_name", "email"
).FROM(
    "employees"
).WHERE(
    "email = 'someone@example.com'"
).run()

```

!!!info "Identifiers ONLY"
    It is advisable to limit use of strings to only identifiers e.g. `column names`, `table names`, `...`
    and operators `=`, `<>`, `<` etc.


!!!danger "Magic Literals Are Bad"
    It is usually not advisable to repeat string or other constants in multiple places across your codebase.
    If you notice string or literal values repeating more than once consider turning them into constants.


&nbsp;
&nbsp;
## Okay... How about inserting Data?

Adding or inserting data with SuperSQL is just as easy as querying data.

However it is important for you to understand that __SuperSQL is NOT AN ORM__, and that means you
can't use some magical `table.save()` method to insert data to the database.

That's now how we roll... &nbsp; &nbsp; :smile:

So how then do you insert data? Let's look at some code.

```py
# borrowing Query and Employee code from above
...

def insert(**kwargs):
    result = query.INSERT(
        emp
    ).VALUES(
        **kwargs
    ).execute()


def bulk_insert(*args):
    result = query.INSERT(
        emp.first_name,
        emp.last_name,
        emp.email
    ).VALUES(
        args
    ).execute()


def insert_with_into(*args):
    # Use of INTO(table) used here is 100% optional but arguably
    # adds readability
    results = Query.INSERT(
        emp.first_name, emp.last_name, emp.email
    ).INTO(
        emp
    ).VALUES(
        ["John", "Doe", "john.doe@example.net"] if not args else args
    ).execute()

query.INSERT().INTO().VALUES().WHERE_NOT_EXISTS()
```

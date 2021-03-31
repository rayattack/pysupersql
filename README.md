Supersql Library
================
There are many great database tools for python (i.e. databases, SQLAlchemy, PeeWee etc.) - **but there is no Python tool for databases.**

In addition you might have come to the same realisation and thinking the following:

1. But we don't want to use an ORM

2. Why can't we get a low level pythonic, powerful SQL api with with semantic interaction primitives

3. Async and Sync support should be supported

Supersql checks all those boxes and more. It is a python superset of SQL - allowing you leverage the full power of python to
write advanced SQL queries.

&nbsp;

**Tutorial**: [Open Documentation](https://rayattack.github.io/supersql/)

**Requirements**: Python 3.6+

&nbsp;


### NOTE: Still Very Much In Development

```sql
SELECT * FROM customers ORDER BY last_name ASC LIMIT 5
```


```py
# query.SELECT('*') is the same as query.SELECT() or query.SELECT(customers)
query.SELECT().FROM(customers).ORDER_BY(-customers.last_name).LIMIT(5)
```

&nbsp;

## Why?
Let's be honest:

1. Writing sql templates using string formatting is really painful.
2. Sometimes an ORM is not what you need, and whilst the new
`f strings` in python solve a lot of problems, complex SQL templating is not of
them.

3. Supersql makes it super simple to connect to and start querying a database in python.

&nbsp;

Let the code do the explanation:
```py

from supersql import Query


query = Query('postgres://user:password@hostname:5432/database')


# Without table schema discovery/reflection i.e. using strings -- NOT OPTIMAL
results = query.SELECT(
        'first_name', 'last_name', 'email'
    ).FROM(
        'employees'
    ).WHERE('email = someone@example.com').execute()

for result in results:
    print(result)


# reflect table schema and fields into a python object for easy querying
emps = query.database.table('employees')

records = query.SELECT(
        emps.first_name, emps.last_name, emps.email
    ).FROM(
        emps
    ).WHERE(emps.email == 'someone@example.com').execute()
```

&nbsp;

What about support for Code First flows? Also supported using Table objects
```py
from supersql import Table, Varchar, Date, Smallint

class Employee(Table):
    """
    SuperSQL is not an ORM. Table only helps you avoid magic
    literals in your code. SuperSQL is not an ORM
    """
    __pk__ = ('email', 'identifier')

    identifier = Varchar()
    email = Varchar(required=True, unique=None, length=25)
    age = Smallint()
    first_name = String(required=True)
    last_name = String(25)
    created_on = Date()


# Now lets try again
emp = Employee()
results = query.SELECT(
    emp.first_name, emp.last_name, emp.email
).FROM(emp).WHERE(
    emp.email == 'someone@example.com'
).execute()
```


&nbsp;


**Note**
---
**Supersql is not an ORM so there is no magic Table.save() Table.find() features nor will they ever be supported.**
The `Table` class is provided only to help with magic literal elimination from your codebase i.e. a query helper and nothing more.

---

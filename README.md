Supersql Library
================

Supersql is a python superset of SQL. It allows you leverage the full power of python to
write your SQL queries.

```sql
SELECT * FROM customers ORDER BY last_name ASC LIMIT 5
```


```py
query.SELECT().FROM(customer).ORDER_BY(-last_name).LIMIT(5)
```

&nbsp;

## Why?
Let's be honest, writing sql templates using string formatting is really painful.
SQLAlchemy is great, but sometimes an ORM is not what you need, and whilst the new
`f strings` in python solve a lot of problems, complex SQL templating is not of
them.

Supersql makes it super simple to connect to and start querying a database in python.

Let the code do the explanation:
```py

from supersql import Connection, Query


connection = Connection('postgres:localhost:5432', user='postgres', password='postgres')

query = Query()


results = query.SELECT(
        'first_name', 'last_name', 'email'
    ).FROM(
        'employees'
    ).WHERE('email', equals='someone@example.com').run()


for result in results:
    print(result)

```

&nbsp;

Too many magic literals? I agree. Let's try that again with a Schema

```py
# Schemas help you remove all those magic literals e.g. 'email' string typed twice
# from your code
from supersql import Schema, String, Date, Integer

class Employee(Schema):
    __pk__ = ('email', 'identifier')

    identifier = UUID(pg='uuid_version1', mysql=None)  # mysql included for examples sake
    email = String(required=True, unique=None, length=25)
    age = Integer()
    first_name = String(required=True)
    last_name = String(25)
    created_on = Date()


# Now lets try again
emp = Employee()
results = query.SELECT(
    emp.first_name, emp.last_name, emp.email
).FROM(
    emp
).WHERE(
    emp.email, equals='someone@example.com'
).run()
```


&nbsp;

# NOTE: Still Very Much In Development -- Expected Launch Date (November 11 2019)

Supersql is not installable until launch

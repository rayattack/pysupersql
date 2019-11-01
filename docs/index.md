# Made For Humans
Supersql is a `very thin wrapper` on top of SQL that enables you write SQL code in python easily.


## Why?
Let's be honest, creating **SQL** templates with string interpolation is really painful.

SQLAlchemy is great, and Supersql is not trying to be a replacement, it just solves a deeper problem - 
it is easier to write simple or complex queries in SuperSQL.

How about 3.6+'s brand
new `f strings`? Yes, they solve a lot of problems, but SQL templating is unfortunately not one of
them.

Supersql makes it super simple to connect to and query data with python.

Just look at the code snippet below:

```py

from supersql import Query

query = Query(
    host='postgres:localhost:5432',
    user='postgres',
    password='postgres'
)

results = query.SELECT(
        'first_name', 'last_name', 'email'
    ).FROM(
        'employees'
    ).WHERE(
        'email', '=', 'someone@example.com'
    ).run()


for result in results:
    print(result)

```

&nbsp;

Too many magic literals? You are right. We can do better. _Let's try that again with a Schema_

```py
# Schemas help you remove magic
# literals e.g. 'email' string typed twice
# and make your code more pythonic
from supersql import Schema
from supersql import (
    Date,
    Integer,
    String,
    UUID,
)


class Employee(Schema):
    __pk__ = ('email', 'identifier')

    identifier = UUID(postgres='uuid_version1')
    email = String(required=True, unique=None, length=25)
    age = Integer()
    first_name = String(required=True)
    last_name = String(25)
    created_on = Date()


# Now lets refactor the previously
# encountered code using the newly discovered
# schema object
emp = Employee()

results = query.SELECT(
    emp.first_name, emp.last_name, emp.email
).FROM(
    emp
).WHERE(
    emp.email == 'someone@example.com'
).execute()  # same as run()
```

## Supersql Empowers the Full Power of SQL in Python

- Complex Queries with Joins
- Support for Athena, Postgres, MySQL, MariaDB, Oracle, MSSQL Server
- Complete Pythonic API to different Databases
- Automatic Connection Pooling
- Preview and Execute Table DDL
- Vendor Translated Functions (MySQL, Oracle, Postgres) Functions
- Cloudformation DDL
- Pythonic Trigger Declarations
- Etc...

&nbsp;

# NOTE: Still Very Much In Development -- Expected Launch Date (November 11 2019)

Supersql is not installable until launch

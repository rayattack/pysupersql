Supersql Library
================

Supersql is `very thin wrapper` on top of SQL that enables you write your SQL code in python easily.


## Why?
The new python f strings and string formatting are nice but not customizable enough. Supersql makes
it super simple to connect to and start querying a database in python.

Let the code do the explanation:
```py

from supersql import Connection, Query

connection = Connection('postgres:localhost:5432', user='postgres', password='postgres')

query = Query()


results = query.SELECT(
    'first_name', 'last_name', 'email').FROM('employees').WHERE('email', equals='someone@example.com').run()

for result in results:
    print(result)



# Schemas help you remove all those magic literals e.g. 'email' string typed twice
# from your code
from supersql import String, Date, Integer

class Employee(Schema):
    __pk__ = ('email', 'identifier')

    identifier = UUID(pg='uuid_version1', mysql=None)  # mysql included for examples sake
    email = String(required=True, unique=None, length=25)
    first_name = String(required=True)
    last_name = String(25)


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

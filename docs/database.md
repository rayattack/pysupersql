# Discovering Database Tables


# DDL via SuperSQL

Supersql is not limited to only querying tables


## Defining Primary & Primary Keys

```py
from supersql import Schema

from supersql import (
    Date,
    Integer,
    String,
    UUID,
)


class Employee_Category(Schema):
    __tablename__ = 'employee_categories'

    identifier = UUID(postgres='uuid_version_4')
    name = String(25)


class Employee(Schema):
    __pk__ = ('email', 'identifier')

    identifier = UUID(pg='uuid_version1', mysql=None)
    email = String(required=True, unique=None, length=25)
    age = Integer()
    first_name = String(required=True)
    last_name = String(25)
    created_on = Date()
```

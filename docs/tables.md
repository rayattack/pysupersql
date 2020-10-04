

Remember (**SuperSQL is not an ORM**) - Repeat this to yourself as many times as you need to.

Supersql `Table` objects have 2 primary uses:

- DDL Template for table create statements.
- Placeholders for table columns to be used as input to the query object.

This means that unlike traditional ORMs you can not do things like `table.save()`, `table.query()` or `table.id = 1000`.


Why then is a table so important?

- Reduce Bugs and Errors as Tables are SQL aware constant declarations
    ```py
    from supersql import Query
    from supersql import Table
    from supersql import String, Serial

    class Account(Table):
        identifier = Serial(pk=True, required=True)
        username = String(25, required=True)
        email = String(50, unique=True)
        password = String(512, required=True)
        age = Integer(validator=is_underage)

        def is_underage(self, age):
            # supersql will call this method before
            # sending value to database
            return age < 18


    query.CREATE_TABLE(Account)


    # without Table schema you would have to type out
    # the following explicitly
    query.CREATE_TABLE("account").COLUMNS(
        "identifier serial PRIMARY KEY NOT NULL",
        "username varchar(50) NOT NULL",
        "email varchar(50)",
        "password varchar(512)"
    ).CONSTRAINT(
        "ux_email_username UNIQUE(email, username)"
    )
    ```
- Table objects allow you to use pythonic comparisons to generate SQL commands
    ```py
    account = Account()
    query.SELECT().FROM(account).WHERE(account.created_at == python_datetime)
    ```

## Table Supported Datatypes

A query object can be created as an orphan (useful in scenarios where simple SQL
syntax generation is desired) or as a connected query (with database connection
 config).


### Boolean
Represents Truthy or Falsy values i.e. True/False, Yes/No, 1/0 etc.

### Datetime
Represents all Date, Time, and Timestamp types with support for Naive or Aware
python datetime objects.

- date
- datetime2 (mssql)
- datetime
- datetimeoffset (mssql)
- smalldatetime (mssql)
- time
- timestamp (postgres, mysql)
- interval (postgres)
- year (mysql)

### Integer
Represents all non decimal numbers.

- integer
- smallint
- Money
- etc.

### Float
Represents all non integer numeric values.

### String
Represents varying/variable character arrays, text and alphanumeric values.

- char
- varchar
- text
- enum
- set (mysql)
- etc.

### UUID
Represents the Universally Unique Identifier type.

### JSONB
Maps to key value collection on databases that support JSON storage. 

### Array
Maps to an array of other valid database types on supported vendor engines.

### Spatial
Correlates to positional, geographic data types i.e. point, coordinates etc.

### Network
Mac addresses, INET etc data types.

```py
from supersql import Table
from supersql import String

class Example(Table):
    username = String()
```

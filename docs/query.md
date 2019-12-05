# What is a Query?

At the heart of it SuperSQL can simply be viewed as a query generator and database
connection proxy. It provides a highl level *__Query__* object and all interactions
with databases happen via this object.

!!!info "Available High Level Imports"
    There are only 2 imports you will ever need to make no matter no matter how
    your query needs are, and this correspond to the only high level imports made
    available by the library.

```py
from supersql import Query
from supersdql import Table

```

For now let us focus on the `supersql.Query` object.


## Create a SuperSQL Query

A query object can be created as an orphan (useful in scenarios where simple SQL
syntax generation is desired) or as a connected query (with database connection
 config).



!!!info "Specifying A Dialect"
    Irrespective of the query type i.e. `orphaned` or `connected` you are advised
    to provide an SQL dialect - i.e. the database you are targeting, as to ensure
    the SQL generated is valid for the eventual database engine.


### Orphan Query

```py
from supersql import Query

query = Query()  # no dialect provided
query_with_dialect = Query(dialect="postgres")

```

An orphan Query is one with no parent database specified i.e. It is not connected
to a database and as such can only be used to generate SQL statements. It is advisable
to always provide a __`dialect`__ when initializing a Query so that the correct syntax can
be targeted if you eventually decide to connect the Query to a database server.

Supported dialects are:

- postgres
- oracle
- mysql `or` mariadb
- oracle
- athena
- mssql


### Connected Query

```py
from os import environ
from supersql import Query

dialect = "postgres"
user = "postgres"
pwd = "strong.password.here"
db = "northwind"
host = "localhost"
port = 5432

query = Query(
    dialect=dialect,
    user=user,
    password=pwd,
    database=db,
    host=host
)
# or
query2 = Query(dialect, user, pwd, database, host, port)

```

Unlike orphaned queries, connected queries can be used to retrieve results/data from
the database server engine.

To create a connected query pass in additional parameters to the Query constructor:

- *__dialect__*: What database dialect are you targeting. __`str`__
- *__user__*: The database user to connect as. __`str`__
- *__password__*: The database password for the provided user. __`str`__
- *__host__*: The IP address or hostname where the database lives with optional
    port information i.e. `localhost` or `localhost:5432` are both valid values. __`str`__
- *__port__*: Optional port information (ignored if port is found in `host` string). __`int`__
- *__database__*: The name of the target database on the host. __`str`__

&nbsp;



&nbsp;

## Query Command API

SuperSQL supports almost all SQL commands and the goal is to support all SQL commands
before v2020.1 comes out.

SQL commands supported as at v2019.3 includes:

- SELECT
- FROM
- WHERE
- GROUP_BY
- ORDER_BY
- AS
- IN
- JOIN
- HAVING
- LIMIT
- FETCH
- OFFSET
- BETWEEN
- FUNCTION
- WITH
- WITH_RECURSIVE
- UPSERT
- INSERT
- CREATE (tables, databases, extensions, views, triggers, schemas, functions etc.)
- DROP
- UPDATE
- AND
- OR
- CAST
- UNION
- UNION_ALL

For a full list of supported SQL constructs with code examples take a look at the
[SuperSQL Command Reference](#api-command-reference).


## How Query Commands Work?

Every query object you create will have all the SQL commands functions as a python method with
CAPITALIZED method names, let us nickname these capitalized methods __`sqlproxies`__.

Perhaps it is more important to note that __`sqlproxies`__ are chainable and always return an
instance of the same query object with the exception of __SELECT__ and __WITH__ queries.

!!!note "SELECT, WITH, and WITH RECURSIVE returns a new Query instance"
    Whilst __`sqlproxies`__  return the same query object - __SELECT does not__.
    
    It creates a clone of the original query object so every select or subquery
    select has its own new slate from which to build and execute queries. This is necessary
    so you don't have to instantiate new query objects in subqueries.

    You can take a look at the implementation on github to see how SELECT differs from the
    other __`sqlproxies`__

```python
from supersql import Query

query = Query(...)  # connection params as required

emp = query.database("mydbname").tables().get("employee")

select_all = Query.SELECT().FROM(emp)
select_all_str = Query.SELECT("*").FROM("employee")
select_all_schema = Query.SELECT(emp).FROM(emp)

```


### Executing Queries

```py
from supersql import Query
from mycodebase.schemas import Employee

query = Query(...)
emp = Employee()

statement = query.SELECT(
    emp.first_name, emp.last_name, emp.age, emp.email
).FROM(
    emp
).WHERE(
    emp.email == "john.doe@example.org"
)

results = statement.execute()
```

Executing queries will return an `iterable` python object that is an instance of the
`supersql.core.result.Result` python class.


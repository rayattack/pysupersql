```py

from supersql import Query, Schema
from supersql import String


q = Query(user="postgres", password="password", host="localhost/mydb")


class Customer(Schema):
    __tablename__ = "customers"

    name = String()  # when you use string without arguments it defaults to text data type
    email = String(50)  # this will be a varchar(50) because a limit is given
    description = String()
    store = String()


cust = Customer()

prep = q.DISTINCT(
    cust.name,
    cust.email
).FROM(
    cust
).WHERE(
    cust.store == '2'
)

results = prep.run()


distinc_on_prep = q.DISTINCT(
    cust.name,
    cust.email,
    ON=cust.name
).FROM(
    cust
).ORDER_BY(
    cust.name,  # must come first due to postgres rules for distinct on order by usage
)

distinct_on_results = distinc_on_prep.run()


sqlbutler = q.SELECT(
    cust.name,
    cust.description,
    cust.email
).FROM(
    cust
).WHERE(
    cust.email == 'one@example.com'
)

results = sqlbutler.run()


in_select = q.SELECT(
    cust.name,
    cust.email,
    emp.name
).FROM(
    cust,
    emp
).WHERE(
    cust.name in ("Anna", "Laura", "Everett", "Peter")
)


and_select = q.SELECT(
    cust.name,
    cust.email
).FROM(
    cust
).WHERE(
    cust.name == 'mary' & cust.email % '%yahoo.com'
)


limit_select = q.SELECT(
    cust
).WHERE(
    cust.age > 5
).ORDER_BY(
    +cust.age,  # ASC
    -cust.name  # DESC
).LIMIT(
    3
).OFFSET(
    1
)
```

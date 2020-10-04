
```py

from supersql import Table
from supersql import Query

from examples import config

from examples.tables.customer import cust

query = Query(**config)


where = query.SELECT(
    cust
).FROM(
    cust
).WHERE(
    cust.active == True &
    cust.address_id == 45
)

alt_where = query.SELECT(
    cust
).FROM(
    cust
).WHERE(
    cust.active == True
    & cust.address_id == 45
    & cust.customer_id == 4
    | cust.create_date > '2019-09-30'
)

```
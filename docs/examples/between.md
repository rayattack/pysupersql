
```py
from supersql import Query

from .schemas.rental import rental
from .schemas.customer import cust


q = Query()


# YOU CAN OMIT FROM at the expense of less readability for others)
between_select = q.SELECT(
    cust
).WHERE(
    cust.store_id > 5 & cust.store_id < 10
)

alt_between_select = q.SELECT(
    cust
).WHERE(
    cust.store_id.BETWEEN(5,10) & cust.email in ('one@g.com', 'two@y.com', 'three@o.com')
)

alt_select = q.SELECT(
    cust.first_name
).FROM(
    cust
).WHERE(
    cust.store_id > 3 & cust.store_id < 5
).AND(
    cust.email.IN('one@g.com', 'two@y.com', 'three@o.com')
).OR(
    cust.email in ()
)

```
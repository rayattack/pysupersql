from supersql import Query

from examples import config
from examples.schemas.customer import cust
from examples.schemas.staff import staff


q = Query(**config)


union = q.SELECT(
    cust.first_name,
    cust.last_name,
    "customer as type"
).FROM(cust).UNION(
    q.SELECT(
        staff.first_name,
        staff.last_name,
        "customer as type"
    ).FROM(
        staff
    )
)


union_all = q.SELECT(
    q.X(cust.first_name + " " + cust.last_name).AS("full_name")
).FROM(
).UNION_ALL(
)


prep = q.SELECT().FROM(cust).WHERE(cust.email in ('hou@one.com', 'won@thes.co'))
sql_string = prep.sql

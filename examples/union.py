from supersql import Query

from examples import config
from examples.schemas.customer import cust
from examples.schemas.staff import staff


q = Query(**config)


union = q.SELECT(
    cust.first_name,
    cust.last_name,
    cust.LITERAL("customer").AS("type")
).FROM(cust).UNION(
    q.SELECT(
        staff.first_name,
        staff.last_name,
        q.LITERAL("customer").AS("type")
    ).FROM(
        staff
    )
)


union_all = q.SELECT(
    cust.first_name + " " + cust.last_name
).AS(
    "full_name"
).SELECT(
    q.LITERAL("")
)


prep = q.SELECT().FROM(cust).WHERE(cust.email in ('hou@one.com', 'won@thes.co'))
sql_string = prep.sql

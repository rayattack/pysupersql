

from supersql import Query

from examples import config


q = Query(**config)


exc = q.SELECT(
    "*"
).FROM(
    "table"
).EXCEPT(
    q.SELECT()
)
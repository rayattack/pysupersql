from supersql import Query

from .schemas.actor import actor
from .schemas.payment import paym

q = Query()


grouped = q.SELECT(
    actor
).FROM(
    actor
).GROUP_BY(
    actor.actor_id
)


g = q.SELECT (
    q.COUNT('*'),
    paym.customer_id
).FROM (
    paym
).GROUP_BY (
    paym.customer_id
).ORDER_BY (
    paym.customer_id
)

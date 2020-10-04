
```py

from supersql import Query

from .schemas.actor import actor


q = Query()


is_null = q.SELECT(
    actor
).FROM(
    actor
).WHERE(
    actor.actor_id is not None
)


is_null = q.SELECT(
    actor
).FROM(
    actor
).WHERE(
    actor.actor_id is None
)


```
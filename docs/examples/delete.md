
```py

from supersql import Query


from src.examples import config
from src.examples.tables.actor import actor


query = Query(**config)


sql = query.DELETE_FROM(actor).WHERE(
	actor.first_name == 'John'
).AND(
	actor.last_name == 'Doe'
)
results = sql.execute()


sql = query.DELETE(actor).WHERE(
	actor.id == 1
)
results = sql.execute()


```
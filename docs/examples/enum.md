
```py

# Postgres specific


from supersql import Query
from supersql import Timestamp


from supersql.examples import config


query = Query(**config)


query.CREATE_TYPE("rainbow").AS_ENUM({"red", "orange", "yellow", "green", "blue", "purple"})


```
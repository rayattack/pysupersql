
```py
from supersql import Query


from examples import config


q = Query(**config)


select_command = q.SELECT(*).FROM("customers")

command = q.DECLARE("my_custom_cursor").CURSOR().FOR(
    select_command
)
# which is same as
alternate_command = cursivator(select_command)


def cursivator(query, cursor_name="my_cursor_name"):
    return q.DECLARE(cursor_name).CURSOR().FOR(query)


first_100_results = command.NEXT(100)  # or command.FETCH_NEXT(x) or command.FETCH(x)
prior_100 = command.PRIOR(100)  # or command.FETCH_PRIOR(x)

```
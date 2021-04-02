from supersql import Query

from .schemas.actor import actor
from .schemas.film import film


q = Query()


add_concat_alias = q.SELECT(
    actor.first_name + " " + actor.last_name
).AS(
    "alias_name"
).FROM(
    actor
)

alt_concat_alias = q.SELECT(
    actor.first_name,
    " ",
    actor.last_name
).AS(
    "alias_name"
).WHERE(
    actor.actor_id in (4,5)
)

# This query will also work because you are selecting
# from actor i.e. SELECT first_name AS column_alias FROM actor;
# The where and from are optional in such a case;
alt = q.SELECT(
    actor.first_name.AS("column_alias")
)


# No support for table aliases as it is unncessary
# e.g. SELECT f.name, f.age FROM for_a_very_long_table_name AS f;
# but if we wanted to suppor it it might look like
unsupported_q = q.SELECT(
    "f.first_name",
    "f.last_name"
).FROM(
    actor.AS("f")
)

# And for join would have been thus if supported
unsupported_q = q.SELECT(
    "f.actor_id",
    "a.actor_id"
    "f.last_name"
).FROM(
    film.AS("f")  # or all text i.e. 'actor as f'
).JOIN(
    actor.AS("a") # can also use all text, but what's the point then?
).ON(
    film.actor_id == actor.actor_id
)
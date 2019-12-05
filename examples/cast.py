
from supersql import Query, Date, CAST
from datetime import date

from supersql.functions import CAST, SUM, COUNT

from .tables.actor import Actor
from .tables.film import Film, ActorFilm
from .tables.customer import cust
from .tables.rental import rental


query = Query()
actor = Actor()
actor_film = ActorFilm()

f = query.FUNCTION()


query_cast = query.SELECT(
    actor.actor_id,
    actor.first_name
).FROM(
    actor
).WHERE(
    f.cast(actor.last_update).AS(Date) == '2005-05-27'
)

shorthand_cast = query.SELECT(
    actor.actor_id,
    actor.first_name
).FROM(
    actor
).WHERE(
    actor.last_update.AS(Date) == '2005-05-27'  # shorthand syntax, notice the absence of f.CAST
)


function_cast = query.SELECT(
    cust.first_name,
    cust.last_name
).WHERE(
    cust.customer_id in query.SELECT(
        cust.customer_id
    ).FROM(
        rental
    ).WHERE(
        f.cast(rental.return_date).AS(date) == '2005-05-27'
    )
)

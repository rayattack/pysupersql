
from supersql import Query, Date, CAST
from datetime import date

from supersql.functions import CAST, SUM, COUNT

from .schemas.actor import Actor
from .schemas.film import Film, ActorFilm
from .schemas.customer import cust
from .schemas.rental import rental


query = Query()
actor = Actor()
actor_film = ActorFilm()


query_cast = query.SELECT(
    actor.actor_id,
    actor.first_name
).FROM(
    actor
).WHERE(
    query.CAST(actor.last_update).AS(Date) == '2005-05-27'
)

shorthand_cast = query.SELECT(
    actor.actor_id,
    actor.first_name
).FROM(
    actor
).WHERE(
    actor.last_update.AS(Date) == '2005-05-27'  # shorthand syntax, notice the absence of query.CAST
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
        CAST(rental.return_date).AS(date) == '2005-05-27'  # using function import
    )
)

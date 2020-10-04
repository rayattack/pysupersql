
```py


from supersql import Query


from .schemas.actor import Actor
from .schemas.film import Film, ActorFilm


query = Query()
actor = Actor()
actor_film = ActorFilm()


pythonic_in = query.SELECT(
    actor.actor_id,
    actor.first_name
).FROM(
    actor
).WHERE(
    # CAVEAT: Might not work across python ports as it unwinds callstack
    # as a hack to achieve this pythonic workaround
    # 
    # Kindly use sqllike in below as much as possible
    actor.actor_id in query.SELECT(
        actor_film.actor_id
    ).FROM(
        actor_film
    )
)


sqllike_in = query.SELECT(
    actor.actor_id,
    actor.first_name
).FROM(
    actor
).WHERE(
    actor.actor_id.IN(
        query.SELECT(
            actor_film.actor_id
        ).FROM(
            actor_film
        )
    )
)


```
from supersql import Schema
from supersql import (
    ForeignKey,
    Integer,
    Number,
    String,
    Timestamp,
)


class ActorFilm(Schema):
    __tablename__ = 'actor_film'

    actor_id = ForeignKey(Integer())
    film_id = ForeignKey(Integer())
    last_updated = Timestamp()


class Film(Schema):
    film_id = Integer()
    title = String(255)
    description = String()
    release_year = Integer()
    language_id = Number(5)  # number of digits allowed
    rental_duration = Number(2)  # number of digits allowed
    rental_rate = Number(4,2)  # number of digits allowed
    length = Number()
    replacement_cost = Number(5,2)
    rating = String()
    last_update = Timestamp()


film = Film()

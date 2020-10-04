from supersql import Schema
from supersql import (
    Integer,
    Number,
    String,
    Timestamp,
)


class Actor(Schema):
    __tablename__ = 'actor'
    
    actor_id = Number()
    first_name = String(45)
    last_name = String(45)
    last_update = Timestamp()


actor = Actor()

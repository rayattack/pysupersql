"""
To insert you use the q.INSERT_INTO method or it's
shorthand alias q.INSERT
"""
from supersql import Schema, Query
from supersql import (
    String,
    Integer
)


query = Query("postgres:localhost:5432")


class Fruit(Schema):
    __tablename__ = 'fruits'

    name = String(25)
    price = Integer()
    category = String(25)


class Nuts(Schema):
    name = String(25)
    price = Integer()
    description = String(250)


fruits = Fruit()
nuts = Nuts()


prep = query.INSERT(
    fruits.name,
    fruits.price
).VALUES(
    ("Banana", 25.04,),
    ("Mango", 33.00),
    ("Apple", 22.00)
)

insert_from_table = query.INSERT(
    nuts.name,
    nuts.price
).INTO(
    nuts
).VALUES(
    query.SELECT(
        fruits.name,
        fruits.price
    ).FROM(
        fruits
    ).WHERE(
        fruits.description == "nuts"
    )
)

shorthand_insert = query.INSERT(
    nuts.name,
    nuts.price
).VALUES(
    ("Bambara", 3.01)
)


explicit = query.INSERT_INTO(
    nuts
).VALUES(
    ... #Your values here, can be one or more lists/tuples
)


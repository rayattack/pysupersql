from supersql import Query, Schema
from supersql import (
    Integer,
    String,
    UUID
)



query = Query(
    vendor="postgres",
    host="localhost:5432",
    database="northwind",
    user="postgres",
    password="postgres"
)


class Movies(Schema):
    identifier = UUID()
    name = String()
    rating = Integer(datatype='integer')

movies = Movies()


update_movies_table = query.UPDATE(
    Movies()
).SET(
    movies.name
).VALUES(
    "The Good, The Bad, The Ugly"
)

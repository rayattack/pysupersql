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
    (movies.name, "value"),
    (movies.age, "value")
).VALUES(
    "The Good, The Bad, The Ugly"
)


class cemp:
    pass

q = query
value = ""

q.UPDATE(cemp).SET(cemp.name, cemp.age).VALUES("Yeti", 4)
q.UPDATE(cemp).SET(
    (cemp.name, value),
    (cemp.age, value),
    (cemp.other_key, value)
).WHERE(
    cemp.name == "something"
)

q.UPDATE(cemp).SET(zip(cemp.keys(), range(5)))

# method 1: pass in a dictionary of columnname: value - s
q.UPDATE(cemp).SET({
    cemp.age: value
})

# method 1 alsoa allows you to pass in any object
# that implements a `to_dict` method where
# this method returns a dictionary of key value pairs
cemp = cemp()
cemp.first_name = "some"
cemp.age = 45
q.UPDATE(cemp).SET(cemp)

class Customer:...
customer = Customer()

# method 2: pass in a string
q.UPDATE("tablename").SET(f"first_name = '{customer.first_name}', age = {customer.age}")

# final method
q.UPDATE(cemp).SET(cemp.age << 4, cemp.first_name << "")

# in the set method inspect each data attribute and raise error if not assigned a value yet
q.UPDATE(cemp).SET(cemp.age = 55, cemp.first_name = "John", cemp.last_name = "Doe")


q.CREATE_OR_REPLACE_MATERIALZED_VIEW()
q.CREATE_MATERIALIZED_VIEW()

from supersql import Schema
from supersql import (
    ForeignKey,
    Integer,
    Number,
    String,
    Timestamp,
)

class Rental(Schema):
    rental_id = Integer()
    rental_date = Timestamp(timezone='GMT+1')
    inventory_id = Integer()
    customer_id = Integer()
    return_date = Timestamp()
    staff_id = Integer(5)
    last_update = Timestamp()


rental = Rental()

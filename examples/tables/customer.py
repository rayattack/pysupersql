from supersql import Schema
from supersql import (
    Boolean,
    Bytes,
    Integer,
    Number,
    String,
    Timestamp,
)


class Customer(Schema):
    __tablename__ = 'staff'

    customer_id = Integer()
    store_id = Number(3)
    first_name = String(45)
    last_name = String(45)
    email = String(50)
    address_id = Integer(5)
    activebool = Boolean()
    create_date = Timestamp()
    last_update = Timestamp()
    active = Integer(2)


cust = Customer()

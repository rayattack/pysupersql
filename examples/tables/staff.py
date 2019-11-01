from supersql import Schema
from supersql import (
    Boolean,
    Bytes,
    Integer,
    Number,
    String,
    Timestamp,
)


class Staff(Schema):
    __tablename__ = 'staff'

    staff_id = Integer()
    first_name = String(45)
    last_name = String(45)
    address_id = Integer(5)
    email = String(50)
    store_id = Number(3)
    active = Boolean()
    username = String(16)
    password = String(50)
    last_update = Timestamp()
    picture = Bytes()


staff = Staff()

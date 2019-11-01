from supersql import Table
from supersql import Integer, String, Timestamp


class Payment(Table):
    payment_id = Integer()
    customer_id = Integer(fk="table.column")
    staff_id = Integer(fk="table.column")
    rental_id = Integer(fk="table.column")
    amount = Integer()
    payment_date = Timestamp()


paym = Payment()

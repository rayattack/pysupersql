"""
A join specifies which table is the Boss

LEFT JOIN = Left table is the boss, join right table and if empty show null values
RIGHT JOIN = Right table is the boss, join left and if empty show null

join/inner join - both tables are the boss
"""

from supersql import Query, Schema
from supersql import Integer, String, Timestamp

from .schemas.customer import cust
from .schemas.payment import paym
from .schemas.staff import staff

class Alpha(Schema):
    __tablename__ = 'alpha'
    id = Integer()
    name = String()
    description = String()
    last_update = Timestamp()


# Let's imagine for some weird reason you want to
# inherit the same fields as a previous schema

class Beta(Alpha):
    __tablename__ = 'beta'

    # remove description and add price to thi
    __exclude__ = 'description'
    price = Integer()


q = Query()
a = Alpha()
b = Beta()


insert_alpha_fruits = q.INSERTINTO(
    a.name
).VALUES(
    (1, 'Apple'),
    (2, 'Orange'),
    (3, 'Pineapple'),
    (4, 'Manago')
)

insert_beta_fruits = q.INSERTINTO(
    b.id,
    b.name
).VALUES(
    # using zip for effect to show power available to supersql from python
    zip((1,2,3,4), ('Orange', 'Mango', 'Apple', 'Banana'))
)


joined = q.SELECT(
    a.id,
    a.name,
    b.name.AS("second_fruit"),
    b.id.AS("second_id")
).FROM(
    a
).JOIN(b).ON(
)


three_way_join = q.SELECT(
    cust.customer_id,
    cust.first_name,
    cust.last_name,
    cust.email,
    paym.amount,
    paym.payment_date,
    staff.first_name,
    staff.last_name
).FROM(
    cust
).JOIN(paym).ON(
    cust.customer_id == paym.customer_id
).JOIN(staff).ON(
    paym.staff_id == staff.staff_id
).WHERE(cust.customer_id == 2)


natural_join = q.SELECT(
    cust
).FROM(cust).NATURAL_JOIN(
    paym
)

natural_join_using = q.SELECT(
    cust
).FROM(cust).JOIN(paym).USING(cust.customer_id)

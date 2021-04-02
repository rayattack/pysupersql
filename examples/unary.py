from supersql import Query, Schema, Varchar, String, Integer, Date


query = Query(vendor='postgres', host='localhost:5432/mydatabase', user='user', password='password')


class Customer(Schema):
    __tablename__ = 'customers'

    first_name = String()
    last_name = Varchar()
    email = String(25)

    age = Integer()


cust = Customer()
emp = Employee()

waitress = select_between = query.SELECT(
    cust.first_name,
    cust.email
).FROM(
    cust
).WHERE(
    cust.email in ("abc")
).ORDER_BY(
    +cust.first_name,
    -cust.email
)


results = waitress.run()

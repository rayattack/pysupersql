from supersql import Table, Query
from supersql import String


q = Query(vendor="postgres")

first_name = "first_name"
last_name = "last_name"

tablename = "customers"
primary_key = "identifier"
identifier = 511


class Customers(Table):
    identifier = String()
    first_name = String()
    last_name = String()
    

def test_from():
    expected = "SELECT first_name, last_name FROM customers WHERE identifier = 511";
    assert expected == q.SELECT(first_name, last_name).FROM(tablename).WHERE(f"{primary_key} = {identifier}").print()


def test_delete():
    expected = "DELETE FROM customer WHERE identifier = 5"
    assert expected == q.DELETE("customer").WHERE("identifier = 5").print()


def test_delete_with_datatype():
    expected = "DELETE FROM customers WHERE identifier = 1000"
    cust = Customers()
    assert expected == q.DELETE_FROM(cust).WHERE(cust.identifier == 1000).print()


def test_and():
    expected = "SELECT identifier FROM customers WHERE identifier = 5 AND first_name = 'Joe'"
    custs = Customers()
    assert expected == q.SELECT(custs.identifier).FROM(custs).WHERE(custs.identifier == 5).AND(custs.first_name == 'Joe').print()

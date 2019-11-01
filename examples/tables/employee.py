from supersql import Schema
from supersql import Integer, String, Timestamp


class Employee(Schema):
    employee_id = Integer(pk=True)
    manager_id = Integer(fk="employee.employee_id")
    full_name = String()
    created_at = Timestamp(tz="GMT+1")


emp = Employee()

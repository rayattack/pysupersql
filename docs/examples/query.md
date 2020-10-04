
```py

from supersql import Query
from supersql import Table
from supersql import Connection

from supersql import String


class Query():

    def __init__(self, *args, **kwargs):
        pass

    def AND(self, *args, **kwargs):
        # do something with parameters passed in
        return self

    def FROM(self, *args):
        # do something with from arguments
        return self

    def GROUP_BY(self, *args, **kwargs):
        # do something with parameters passed in
        return self

    def ORDER_BY(self, *args, **kwargs):
        # do something with parameters passed in
        return self

    def SELECT(self, *args, **kwargs):
        # do something with parameters passed in
        return self

    def WHERE(self, *args, **kwargs):
        # do something with parameters passed in
        return self
    
    def run(self):
        """
        Signifies end of query and send/executes/runs query
        """
        return self.results


connection = Connection.get_connection()
query = Query(connection or 'postgres:localhost:5432', user='postgres', password='postgres')


# Why capitalized?
# - Prevent Python Keywords conflict `from`, `and` etc
# - SQL Convention
query.SELECT(
        'e.identifier', 'e.first_name', 'e.last_name', 'd.identifier'
    ).FROM(
        'Employee as e', 'Department as d'
    ).WHERE(
        'd.department', equals="engineering"
    ).AND(
        'e.first_name', ilike='c%'
    ).ORDER_BY('e.first_name', asc=True)


# Now we can both agree that is a lot of magic literals and omitting
# the `e` from anywhere it expects to see an e.first_name for more
# complex queries will cause an error
#
# Let's fix that with string formatting help from a custom class
# you defined that inherits from Schema

class Employee(Schema):
    __pk__ = 'identifier'

    identifier = UUID(pg='version_1', mysql='')
    first_name = String()
    last_name = String()


class Department(Schema):
    __pk__ = ('identifier', 'email')  # Composite primary key

    name = String(length=25, required=True, unique=None)
    identifier = UUID(version=4)


# Remember this is a schema not a model, you use it as input into
# a Query object to get a Results object `array of model representations`
# every Result object in Results is your model.
# 
# REMEMBER: This is a schema not a model
emp = Employee()
dep = Department()

# Now let's try again with the schema'd classes
results = query.SELECT(
                emp.first_name,
                emp.last_name,
                emp.identifier,
                dep.identifier,
            ).COUNT(
                emp.first_name,
                alias='Tally'
            ).FROM(
                emp, dep
            ).WHERE(
                dep.name, equals='engineering'
            ).AND(
                
            ).ORDER_BY(
                dep.first_name, descending=True
            ).GROUP_BY(

            ).run()


```
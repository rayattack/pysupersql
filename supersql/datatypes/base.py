from datetime import datetime as clock


class Base(object):
    """
    Super class for SQL valid datatypes

    When a column is accessed in a schema then there are a few things that
    supersql expects to happen.

    1. The name of the column is stored as the value
    2. The Column metadata i.e. length, pk ( primary_key ), unique etc are processed
    
    Overriden Operators
    -------------------
    In addition to providing data descriptor functionality, columns also
    override certain logical operators of python to be able to able to
    provide semantic and intuitive usage in the supersql API.

    ```py
    from supersql import Schema, Query

    # where Employee is a class you created
    # that inherits from schema
    from src.schemas.employee import Employee

    query = Query("postgres:localhost:5432")
    emp = Employee()

    query.SELECT('*').FROM(emp).WHERE(emp.name == 'Jon Snow')
    ```

    Given the snippet above it is clear why overriding the `==` equality
    operator is necessary.

    Other overriden operators include:

    - `>` Greater than
    - `<` Less than
    - `!=` Inequality
    - `in` Membership
    - `not in` Exclusion
    - `%` Like

    It is important to note that the modulo operator is overriden to behave
    like it's SQL counterpart i.e. LIKE
    """

    def __init__(self, *args, **kwargs):
        self.pk = kwargs.get("pk")
        self.required = kwargs.get("required")
        self.default = kwargs.get("default")
        self.unique = kwargs.get("unique")
        self.textsearch = kwargs.get("textsearch")
        self.options = kwargs.get("options")
        self.value = None

        self._print = []

        # used to maintain definition order of table schema
        # when SELECT is used/called
        self._abs = clock.now().timestamp()

    def __get__(self, instance, metadata):
        return self

    def __set__(self, instance, value):

        if self.unique:
            instance.uniques = self._name, value
        self.validate(value, instance)
        self.value = value
        instance.__mutated__ = True
        instance.add_field(self, value)

    def __set_name__(self, cls, name):
        self._meta = cls
        self._name = name

    def __add__(self, value):
        pass

    def __eq__(self, value):
        self._print.append(f"{self._name} = {value}")
        return self

    def __ge__(self, value):
        return super().__ge__(value)

    def __gt__(self, value):
        pass

    def __le__(self, value):
        return super().__le__(value)
    
    def __lt__(self, value):
        return super().__lt__(value)
    
    def __mod__(self, value):
        pass
    
    def __ne__(self, value):
        raise NotImplementedError

    def __xor__(self, value):
        pass

    def cast(self, instance, value):
        self.validate(value, instance)
        if isinstance(value, self.py_type):  # pylint: disable=no-member
            return value
        return self.py_type(value)  # pylint: disable=no-member

    def validate(self, value, instance=None):
        pass

    def AS(self, *args, **kwargs):
        pass

    def IN(self, *args, **kwargs):
        pass

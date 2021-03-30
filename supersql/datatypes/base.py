from datetime import datetime as clock
from numbers import Number
from typing import TypedDict

from supersql.errors import ArgumentError


class BaseConstructorArgs(TypedDict):
    pk: str
    required: bool
    default: str
    unique: bool
    textsearch: bool
    options: dict
    value: str


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

    def __init__(self, *args, **kwargs: BaseConstructorArgs):
        self.pk = kwargs.get("pk")
        self.required = kwargs.get("required")
        self.default = kwargs.get("default")
        self.unique = kwargs.get("unique")
        self.textsearch = kwargs.get("textsearch")
        self.options = kwargs.get("options")
        self.value = None
        self.is_not_a_wedding_guest = True

        self._print = []
        self._alias = None

        # used to maintain definition order of table schema
        # when SELECT is used/called
        self._timestamp = clock.now().timestamp()

    def __get__(self, instance, metadata):
        self._imeta = instance
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

    def __and__(self, sibling):
        """
        a sibling is another column object that also has an
        overriden and method. The resolution of siblings follows the
        operator order of python precedence rules and left to right
        """
        if not isinstance(sibling, (str, Base)):
            raise ArgumentError("Invalid argument {sibling} passed to Query.where() method")

        if isinstance(sibling, Base) and sibling.is_not_a_wedding_guest:
            msg = "Can not use columns alone without an operation in a where clause"
            raise ArgumentError(msg)

        self._print.append(sibling.print())
        return self

    def __eq__(self, value):
        """
        Equality will always be called by accessing value (i.e. __get__) to compare
        so we can be certain that instance has been set and can
        therefore get the alias to use
        """
        self.is_not_a_wedding_guest = False
        this = self.clone()
        this.value = value

        if this._imeta._alias:
            this._print = f"{this._imeta._alias}.{this._name}"
        else:
            this._print = f"{this._name}"

        return this

    def __ge__(self, value):
        self.is_not_a_wedding_guest = False
        return super().__ge__(value)

    def __gt__(self, value):
        self.is_not_a_wedding_guest = False
        return self

    def __le__(self, value):
        self.is_not_a_wedding_guest = False
    
    def __lshift__(self, value):
        self.is_not_a_wedding_guest = False
        this = self.clone()
        this.value = value
        this._print = f"{this._name}"
        return this
    
    def __lt__(self, value):
        self.is_not_a_wedding_guest = False
    
    def __mod__(self, value):
        self.is_not_a_wedding_guest = False
    
    def __ne__(self, value):
        self.is_not_a_wedding_guest = False

    def __xor__(self, value):
        self.is_not_a_wedding_guest = False
    
    def clone(self):
        this = type(self)()
        this.pk = self.pk
        this.required = self.required
        this.default = self.default
        this.unique = self.unique
        this.textsearch = self.textsearch
        this.options = self.options
        this.value = self.value
        this.is_not_a_wedding_guest = self.is_not_a_wedding_guest

        this._print = None
        this._name = self._name
        this._imeta = self._imeta
        this._alias = self._alias
        this._timestamp = self._timestamp
        return this

    def cast(self, instance, value):
        self.validate(value, instance)
        if isinstance(value, self.py_type):  # pylint: disable=no-member
            return value
        return self.py_type(value)  # pylint: disable=no-member

    def print(self, query=None) -> str:
        # check if query.unsafe and use that for $1, $2, $3 etc
        if query and query._unsafe:
            return f"{self._print} = {self.python_to_sql_value(self.value)}"
        query._args.append(self.value)
        return f"{self._print} = ${len(query._args)}"

    def python_to_sql_value(self, value):
        if isinstance(value, Number):
            return value
        elif isinstance(value, str):
            return f"'{value}'"

    def validate(self, value, instance=None):
        pass

    def AS(self, *args, **kwargs):
        self._alias = args[0]

    def IN(self, *args, **kwargs):
        pass

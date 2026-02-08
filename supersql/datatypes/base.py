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
        
        # Validation constraints
        self.minimum = kwargs.get("minimum")
        self.maximum = kwargs.get("maximum")
        self.min_length = kwargs.get("min_length")
        self.max_length = kwargs.get("max_length")
        
        self.value = None
        self.is_not_a_wedding_guest = True

        self._print = []
        self._alias = None
        
        self._operator = "="

        # used to maintain definition order of table schema
        # when SELECT is used/called
        self._timestamp = clock.now().timestamp()

    def validate(self, value, instance=None):
        from supersql.errors import ValidationError
        
        if value is None:
            if self.required:
                raise ValidationError(f"{self._name} is required")
            return

        if self.min_length is not None and hasattr(value, '__len__'):
            if len(value) < self.min_length:
                raise ValidationError(f"{self._name}: Min length {self.min_length}")
        
        if self.max_length is not None and hasattr(value, '__len__'):
            if len(value) > self.max_length:
                raise ValidationError(f"{self._name}: Max length {self.max_length}")
                
        if self.minimum is not None:
            if value < self.minimum:
                raise ValidationError(f"{self._name}: Must be >= {self.minimum}")
                
        if self.maximum is not None:
            if value > self.maximum:
                raise ValidationError(f"{self._name}: Must be <= {self.maximum}")

    def __get__(self, instance, metadata):
        self._imeta = instance
        return self

    def _clone_with_val(self, value, operator="="):
        self.is_not_a_wedding_guest = False
        this = self.clone()
        this.value = value
        this._operator = operator

        # Check if _imeta has _alias (it might be a class or instance)
        if hasattr(this, '_imeta') and getattr(this._imeta, '_alias', None):
            this._print = f"{this._imeta._alias}.{this._name}"
        else: this._print = f"{this._name}"
        return this

    def __set__(self, instance, value):
        if self.unique: instance.uniques = self._name, value
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
        return self._clone_with_val(value, "=")

    def __ge__(self, value):
        return self._clone_with_val(value, ">=")

    def __gt__(self, value):
        return self._clone_with_val(value, ">")

    def __le__(self, value):
        return self._clone_with_val(value, "<=")
    
    def __lshift__(self, value):
        return self.__eq__(value)
    
    def __lt__(self, value):
        return self._clone_with_val(value, "<")
    
    def __mod__(self, value):
        return self._clone_with_val(value, "LIKE")
    
    def __ne__(self, value):
        return self._clone_with_val(value, "!=")

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
        this._operator = getattr(self, '_operator', '=')

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

    def print(self, query=None):
        # check if query.unsafe and use that for $1, $2, $3 etc
        op = getattr(self, '_operator', '=')
        
        if query and getattr(query, '_unsafe', False):
            return f"{self._print} {op} {self.python_to_sql_value(self.value)}"
        
        if query:
            query._args.append(self.value)
            # Get placeholder from engine (postgres=$%d, mysql=%s, sqlite=?)
            placeholder = query._db._engine.parameter_placeholder
            if '%d' in placeholder:
                placeholder = placeholder % len(query._args)
        else:
            placeholder = '?'
            
        return f"{self._print} {op} {placeholder}"

    def python_to_sql_value(self, value):
        if isinstance(value, Number):
            return value
        elif isinstance(value, str):
            return f"'{value}'"


    def AS(self, *args, **kwargs):
        self._alias = args[0]

    def IN(self, *args, **kwargs):
        pass

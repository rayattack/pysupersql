"""
Represents all numbers that can be stored/represented via a computer

Integers: Integers have no decimal part i.e. they are discrete whole numbers

Decimals: Have a decimal part i.e. leftside.rightside (34.00) and can be
represented with Number(precision, scale, required=...)
    precision: total length of the integer (4.55) is 3 characters long
        and (3.0) is 2 characters long

    scale: the number of decimals (4.55) has a scale of 2 i.e. rightside digits

If Integers are passed in precision and scale digits they ignore the scale and
precision digits override the `use` parameter
"""

from supersql.errors import ValidationError
from supersql.datatypes.base import Base


BIGINT = "bigint"
BIGSERIAL = "bigserial"
DECIMAL = "decimal"
DOUBLE = "double"
INTEGER = "integer"
NUMERIC = "numeric"
REAL = "real"
SMALLINT = "smallint"
SERIAL = "serial"
SMALLSERIAL = "smallserial"


FLOATS = (
    BIGSERIAL,
    DECIMAL,
    DOUBLE,
    NUMERIC,
    REAL,
    SERIAL,
    SMALLSERIAL,
)

INTEGERS = (
    BIGINT,
    INTEGER,
    SMALLINT,
)

ALLTYPES = FLOATS + INTEGERS



class Number(Base):
    """
    Parent of numeric SQL types for method reuse only.

    Defaults to integer
    """
    def __init__(self, *args, **kwargs):
        _use = kwargs.get("use")
        _precision, _scale = None, None

        self.use = Number.validate(_use)

        if(args):
            _shortcut = list(args)
            _shortcut.append(None)
            _precision, _scale = _shortcut

        super(Number, self).__init__(self, *args, **kwargs)

    @staticmethod
    def sqltype():
        # check for precision and scale
        # if less than 2bytes then use smallint
        pass

    @classmethod
    def validate(cls, use):
        if use is None:
            return INTEGER

        target = cls.__name__.lower()

        if target == 'number' and use in ALLTYPES:
            return target
        elif target == 'decimal' and use in FLOATS:
            return target
        elif target == 'integer' and use in INTEGERS:
            return target
        elif target == 'money' and use == target:
            return target
        raise ValueError


class Decimal(Number):...


class Integer(Number):...


class Money(Number):...

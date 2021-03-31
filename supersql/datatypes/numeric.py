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


    def validate(self, value, instance=None):
        """
        Run validation of numeric constraints
        """
        # Ensure only numeric values i.e. float and int are allowed to be assigned
        # as values.
        # Coercion is false by default as to not allow loss of precision unkowingly
        # or silently. To coerce int to float and float to int you the coerce
        # attribute of document fields must be explicitly set to true
        if not isinstance(value, (int, float)):
            raise ValueError(f"Non numeric type detected for field {self._name}")

        # Here an inspection of the class is necessary to allow for recognition
        # of the field type and allow the conversion from one numeric type
        # to another numeric type i.e. int -> float -> int as appropriate
        if self.__class__.__name__ == "Integer":
            if isinstance(value, float) and self.coerce:
                return int(value)
            if isinstance(value, float):
                raise ValueError(
                    f"Coercing float {self._name} to int might cause precision, explicitly set coerce to true"
                )

        # Unlike float -> int where precision loss is possible, converting an
        # integer value to float does mot raise a value error
        if self.__class__.__name__ == "Float" and isinstance(value, int):
            return float(value)

        # Apply minimum and maximum equality checks only after ensuring
        # that the correct datatypes were passed in taking the possibility
        # of absent minimum and maximum validataion parameter from the
        # numeric document field definition
        if self.minimum and value < self.minimum:
            raise ValidationError(
                f"{self._name} has value lower than minimum constraint"
            )
        if self.maximum and value > self.maximum:
            raise ValidationError(
                f"{self._name} has value higher than maximum constraint"
            )
        return value


class Bigint(Number):...

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

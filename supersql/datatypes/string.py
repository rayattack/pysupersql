from supersql.errors import ValidationError
from supersql.datatypes.base import Base


class Char(Base):...


class String(Base):
    @property
    def precision(self):
        """
        Look at the args and keyword args and use the vendor selected
        to generate the right constraints.

        Possible constraints can come from:
            - args[0..n] like 25 signifying that the maximum length of varchar should be this number
            - kwarg['default'] i.e. the default value to be used for a thing
        """
        return f'({self.arguments[0]})' if self.arguments else ''


class Text(Base):...


class Varchar(Base):...

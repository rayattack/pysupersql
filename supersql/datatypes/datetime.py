from supersql.datatypes.base import Base


class Date(Base):...


class Interval(Base):
    def __init__(self, *args, **kwargs):
        self._precision = kwargs.get("precision")


class Time(Base):...


class Timestamp(Base):...

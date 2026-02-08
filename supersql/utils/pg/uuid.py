from supersql.constants.datatype_parameters import (
    DEFAULT,
    PK,
    PRIMARY_KEY,
    REQUIRED,
)


def ddl(instance):
    pass


def traverser(*arguments):
    count = len(arguments)

    for param in arguments:
        if isinstance(param, (PK, PRIMARY_KEY)):
             pass

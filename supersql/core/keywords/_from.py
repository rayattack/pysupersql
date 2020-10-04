
from supersql.core.table import Table
from supersql.errors import MissingArgumentError


_FROM = " FROM "


def FROM(*args, **kwargs):
    this = kwargs.get('this')
    this._callstack.append(_FROM)

    num_of_args = len(args)
    num_of_tables = len(this._tablenames)
    # msg = f"Found different tables in SELECT statement but only 1 command received in FROM"
    msg = f"tables:{num_of_tables}, args:{num_of_args}"

    # if num_of_args != num_of_tables:
    #     raise MissingArgumentError(msg)
    
    for source in args:
        has_alias = None
        if isinstance(source, str):
            _a = None
            _q = str
        elif isinstance(source, type(this)):
            _a = source._alias
            _q = f"({source.print()})"
        elif isinstance(source, Table):
            _a = source._alias
            _q = source.__tn__()

        _from = f"{_q} AS {_a}" if _a else f"{_q}"
        this._from.append(_from)

    _sql = ", ".join(
        [f"{table}" for table in this._from]
    ) if len(this._from) > 1 else "".join(table for table in this._from)
    this._sql.extend([_FROM, _sql])

    return this

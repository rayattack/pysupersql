from supersql.errors import ArgumentError


_FROM = " FROM "
_WHERE = " WHERE "


def WHERE(*args, **kwargs):
    this = kwargs.get('this')
    condition = kwargs.get('condition')

    import pdb; pdb.set_trace()

    if _FROM not in this._callstack:
        tablenames = this._tablenames
        this = this.FROM(*tablenames)

    this._callstack.append(_WHERE)
    this._sql.append(_WHERE)

    if isinstance(condition, str):
        this._sql.append(condition)
    else:
        try:
            this._sql.append(condition.print())
        except AttributeError:
            msg = "Where clause can only process strings or column comparison operations"
            raise ArgumentError(msg)

    return this

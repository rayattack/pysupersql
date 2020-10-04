from supersql.core.table import Table
from supersql.utils.helpers import get_tablename


_SELECT = "SELECT"


def SELECT(*args, **kwargs):
    """SQL SELECT Proxy
    Mechanism for selecting or specifying subset of data to select
    from a table, expression or subquery

    ```sql
        SELECT * FROM customers WHERE age > 10;
    ```

    ```py
        query = Query("postgres")
        query.SELECT("*").FROM("customers").WHERE("age > 10")

        # with table
        cust = Customer()
        query.SELECT(cust).FROM(cust).WHERE(cust.age > 10)

        # other possible ways to query with
        # a table object
        # from is omitted as it is obvious from `select`
        query.SELECT(cust).WHERE(cust.age > 10)

        # "*" can be omitted as it is default but FROM is no longer obvious
        query.SELECT().FROM(cust).WHERE(cust.age > 10)
    ```
    """
    this = kwargs.get('this')
    this._callstack.append(_SELECT)

    num_of_args = len(args)
    if num_of_args == 0:
        separator = "*"
    elif num_of_args == 1:
        arg = args[0]
        if isinstance(arg, str):
            this._tablenames.add(
                get_tablename(arg)
            ) if get_tablename(arg) != arg else this._orphans.add(arg)
            separator = arg
        elif isinstance(arg, Table):
            separator = "*"
            this._tablenames.add(arg.__tn__())
        else:
            separator = arg._name
            this._tablenames.add(arg._meta.__tn__())
    else:
        cols = []
        for member in args:
            if isinstance(member, str):
                tablename = get_tablename(member)
                this._tablenames.add(get_tablename(member)) if tablename != member else None
                cols.append(member)
            elif isinstance(member, Table):
                this._tablenames.add(member.__tn__())
                cols.extend(member.columns())
            else:
                this._tablenames.add(member._meta.__tn__())
                cols.append(f"{member._meta.__tn__()}.{member._name}")

        separator = ", ".join(
            [col for col in cols]
        )

    _select_statement = f"SELECT {separator}"

    if this._pristine:
        this._sql.append(_select_statement)
        this._pristine = False

    return this

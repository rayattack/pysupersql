from supersql import Query
from supersql import Table

from supersql import Integer, UUID
from supersql import Decimal
from supersql import String


CONFIG = {
    "vendor": "postgres",
    "user": "postgres",
    "password": "postgres"
}

SQL = """CREATE TABLE account (
\tidentifier uuid PRIMARY KEY NOT NULL DEFAULT uuid_generate_v1(),
\tfirst_name varchar(25),
\tlast_name varchar
)"""


query = Query(**CONFIG)


class Account(Table):
    identifier = UUID(default="uuid_generate_v1()", pk=True, required=True)
    first_name = String(25)
    last_name = String()


def test_create_table():
    account = Account()
    assert(query.CREATE(Account, safe=False).print() == SQL)

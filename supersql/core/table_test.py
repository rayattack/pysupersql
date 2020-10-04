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
    identifier  uuid(uuid_version=4) PRIMARY KEY NOT NULL,
    first_name  varchar(25),
    last_name   varchar(25)
)"""


query = Query(**CONFIG)


class Account(Table):
    identifier = UUID(default="uuid_generate_v1()", primary_key=True, required=False)
    first_name = String(25)
    last_name = String(25)


def test_create_table():
    account = Account()
    assert(query.CREATE(Account).print() == SQL)

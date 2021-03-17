from unittest import TestCase

from supersql.utils.helpers import get_tablename

TABLENAME = "tablename"
FOUR = "db.schema.tablename.column"
THREE = "schema.tablename.column"
TWO = "tablename.column"
ONE = "tablename"

class HelpersTest(TestCase):

    def test_get_tablename(self):
        self.assertEqual("tablename", get_tablename(FOUR))
        self.assertEqual("tablename", get_tablename(THREE))
        self.assertEqual("tablename", get_tablename(TWO))
        self.assertEqual("tablename", get_tablename(ONE))
        self.assertEqual(TABLENAME, get_tablename(TABLENAME))

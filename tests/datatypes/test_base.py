from unittest import TestCase

from supersql import Query, Table
from supersql.datatypes.base import Base


class Holder(Table):
    __tablename__ = "holdem"
    first_name = Base()
    last_name = Base()


class T(TestCase):
    def test_base_equality(self):
        h = Holder()
        num = 24
        sql = f"first_name = {num}"
        # self.assertEqual(sql, h.first_name == num)
        base = Base()
        o = h.first_name == 24
        self.assertIsInstance(o, Base)
        self.assertEqual(sql, o.print(Query("postgres", unsafe=True)))

    def test_index(self):
        h = Holder()
        self.assertTrue(h.first_name._timestamp <= h.last_name._timestamp)
    
    def test_alias(self):
        h = Holder()
        self.assertFalse(h.first_name._alias)

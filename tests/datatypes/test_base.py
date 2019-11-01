from unittest import TestCase

from supersql import Table
from supersql.datatypes.base import Base


class Holder(Table):
    first_name = Base()
    last_name = Base()


class T(TestCase):
    def test_base_equality(self):
        h = Holder()
        num = 24
        sql = f"first_name = {num}"
        # self.assertEqual(sql, h.first_name == num)
        base = Base()
        base._name = 4
        self.assertEqual(sql, base)
        print(h.first_name == num)
    
    def test_index(self):
        h = Holder()
        self.assertTrue(h.first_name._abs < h.last_name._abs)

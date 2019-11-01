from unittest import TestCase

from supersql import Query, Table
from supersql import String
from supersql.errors import ArgumentError

from supersql.core.query import SUPPORTED_VENDORS


class Play(Table):
    name = String()
    cryptic_name = String()
    more_cryptic = String()

class Chess(Table):
    name = String()


class T(TestCase):
    def setUp(self):
        self.q = Query("postgres")

    def test_supported(self):
        for vendor in SUPPORTED_VENDORS:
            q = Query(vendor)
            self.assertIsInstance(q, Query)

    def test_unsupported(self):
        with self.assertRaises(NotImplementedError):
            q = Query("mongodb")
    
    def test_vendor_required(self):
        with self.assertRaises(TypeError):
            q = Query()

    def test_select(self):
        self.assertIsNotNone(self.q.SELECT("*"))
    
    def test_print_literal(self):
        _ = "SELECT customer_id, age"
        self.q.SELECT("customer_id", "age")
        self.assertEqual(self.q.print(), _)

    def test_print_table(self):
        sql = "SELECT play.cryptic_name, play.more_cryptic, play.name"
        play = Play()
        self.q.SELECT(play.cryptic_name, play.more_cryptic, play.name)
        self.assertEqual(self.q.print(), sql)
    
    def test_print_all_table(self):
        sql = "SELECT *"
        play = Play()
        self.q.SELECT(play)
        self.assertEqual(sql, self.q.print())
    
    def test_print_all_table_cols(self):
        sql = "SELECT play.name, play.cryptic_name, play.more_cryptic, chess.name"
        empty = ""
        play = Play()
        c = Chess()
        self.q.SELECT(play, c.name)
        prep = self.q.print()
        # space_only = prep.replace(
        #     "SELECT ", empty
        # ).replace(
        #     "play.cryptic_name", empty
        # ).replace(
        #     "play.more_cryptic", empty
        # ).replace(
        #     "play.name", empty
        # ).replace(
        #     "play.more_cryptic", empty
        # ).replace(",", empty).replace(" ", empty)
        # self.assertEqual(space_only, empty)
        self.assertEqual(prep, sql)

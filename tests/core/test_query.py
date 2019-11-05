from unittest import TestCase

from supersql import Query, Table
from supersql import String
from supersql.errors import MissingArgumentError

from supersql.core.query import SUPPORTED_VENDORS
from supersql.core.query import _WHERE, _FROM, _SELECT


NAME = "'GOD is great'"

SELECT = "SELECT play.name, play.cryptic_name, play.more_cryptic, chess.name"
FROM = "FROM play AS play, chess AS chess"
WHERE = f"WHERE chess.name = {NAME}"



class Play(Table):
    name = String()
    cryptic_name = String()
    more_cryptic = String()

class Chess(Table):
    name = String()


class T(TestCase):
    def setUp(self):
        self.q = Query("postgres")
        self.p = Play()
        self.c = Chess()
    
    def test_from(self):
        EMPTY = ""
        play = Play()
        c = Chess()
        with self.assertRaises(MissingArgumentError):
            prep = self.q.SELECT(play, c.name).FROM()
        
        prep = self.q.SELECT(play, c.name).FROM(play, c.AS("chess"))
        self.assertEqual(f"{SELECT} {FROM}", prep.print())

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
        prep = self.q.SELECT("*")
        self.assertIsNotNone(prep)
        self.assertIn(_SELECT, prep._callstack)
    
    def test_select_table(self):
        _ = "SELECT name"
        prep = self.q.SELECT(self.c.name)
        self.assertEqual(prep.print(), _)

        # test _from in table
        self.assertGreater(len(prep._tablenames), 0)

        aprep = self.q.SELECT(self.p, self.c.name)
        self.assertEqual(len(aprep._tablenames), 2)
    
    def test_print_literal(self):
        _ = "SELECT customer_id, age"
        prep = self.q.SELECT("customer_id", "age")
        self.assertEqual(prep.print(), _)

    def test_print_table(self):
        sql = "SELECT play.cryptic_name, play.more_cryptic, play.name"
        play = Play()
        prep = self.q.SELECT(play.cryptic_name, play.more_cryptic, play.name)
        self.assertEqual(prep.print(), sql)
    
    def test_print_all_table(self):
        sql = "SELECT *"
        play = Play()
        prep = self.q.SELECT(play)
        self.assertEqual(sql, prep.print())
    
    def test_print_all_table_cols(self):
        sql = "SELECT play.name, play.cryptic_name, play.more_cryptic, chess.name"
        empty = ""
        play = Play()
        c = Chess()
        prep = self.q.SELECT(play, c.name)
        prep_sql = prep.print()
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
        self.assertEqual(prep_sql, sql)
    
    def test_alias_parsing(self):
        prep = self.q.SELECT(
            "f.someone",
            "a.hyou",
            "y.me"
        )
        self.assertEqual(len(prep._tablenames), 3)

        prep = self.q.SELECT(
            "a.me",
            "you"
        )
        self.assertEqual(len(prep._tablenames), 1)

        prep = self.q.SELECT("us")
        self.assertFalse(prep._tablenames)

    def test_where(self):
        play = Play()
        c = Chess()
        prep = self.q.SELECT(play, c.name).FROM(play, c.AS("chess")).WHERE(
            c.name == NAME
        )
        self.assertEqual(f"{SELECT} {FROM} {WHERE}", prep.print())

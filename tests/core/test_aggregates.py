from unittest import TestCase
from supersql import Query, Table

class TestAggregates(TestCase):
    def setUp(self):
        self.q = Query("postgres")
        self.t = Table("posts").AS("p")

    def test_count_simple(self):
        # Should NOT have OVER() clause by default anymore
        sql = self.q.SELECT(self.q.COUNT(self.t.id)).FROM(self.t).build()
        self.assertEqual(sql, 'SELECT COUNT("p"."id") FROM "posts" AS "p"')

    def test_count_with_over_explicit(self):
        # Explicit .OVER() should still generate OVER clause
        sql = self.q.SELECT(self.q.COUNT(self.t.id).OVER()).FROM(self.t).build()
        self.assertEqual(sql, 'SELECT COUNT("p"."id") OVER () FROM "posts" AS "p"')

    def test_distinct(self):
        sql = self.q.SELECT(self.q.COUNT(self.t.id).DISTINCT()).FROM(self.t).build()
        self.assertEqual(sql, 'SELECT COUNT(DISTINCT "p"."id") FROM "posts" AS "p"')

    def test_filter(self):
        q2 = self.q.SELECT(
            self.q.COUNT(self.t.id).FILTER(self.t.score > 10)
        ).FROM(self.t)
        sql = q2.build()
        self.assertIn('COUNT("p"."id") FILTER (WHERE "p"."score" > $1)', sql)
        self.assertEqual(q2._args, [10])

    def test_distinct_and_filter(self):
        q2 = self.q.SELECT(
            self.q.COUNT(self.t.id).DISTINCT().FILTER(self.t.score > 10)
        ).FROM(self.t)
        sql = q2.build()
        self.assertIn('COUNT(DISTINCT "p"."id") FILTER (WHERE "p"."score" > $1)', sql)
        self.assertEqual(q2._args, [10])

    def test_fx_json_object_postgres(self):
        # Default query is postgres
        q2 = self.q.SELECT(
            self.q.FX.json_object('k', self.t.id)
        ).FROM(self.t)
        sql = q2.build()
        self.assertIn('json_build_object(\'k\', "p"."id")', sql)
        # 'k' is inlined, so args should happen to be empty if only one string arg
        self.assertEqual(q2._args, [])

    def test_fx_json_object_sqlite(self):
        q_sqlite = Query('sqlite')
        q2 = q_sqlite.SELECT(
            q_sqlite.FX.json_object('k', 1)
        )
        sql = q2.build()
        
        # SQLite uses ? and json_object
        # String 'k' is inlined as 'k'
        self.assertIn("json_object('k', ?)", sql)
        self.assertEqual(q2._args, [1])

    def test_fx_generic_function(self):
        q2 = self.q.SELECT(
            self.q.FX.random_func(1, 'a')
        )
        sql = q2.build()
        self.assertIn("random_func($1, 'a')", sql)
        self.assertEqual(q2._args, [1])

    def test_fx_with_alias(self):
        q2 = self.q.SELECT(
            self.q.FX.my_func(1).AS('res')
        )
        sql = q2.build()
        self.assertIn('my_func($1) AS res', sql)
        self.assertEqual(q2._args, [1])

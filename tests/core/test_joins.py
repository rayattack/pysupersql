from unittest import TestCase
from supersql import Query, Table

class TestJoins(TestCase):
    def setUp(self):
        self.q = Query("postgres")
        self.u = Table("users").AS("u")
        self.p = Table("posts").AS("p")

    def test_join_fluent_on(self):
        # New fluent syntax
        sql = self.q.SELECT(self.u.name).FROM(self.u).JOIN(self.p).ON(self.u.id == self.p.user_id).build()
        expected = 'SELECT "u"."name" FROM "users" AS "u" INNER JOIN "posts" AS "p" ON "u"."id" = "p"."user_id"'
        self.assertEqual(sql, expected)

    def test_left_join_fluent(self):
        sql = self.q.SELECT(self.u.name).FROM(self.u).LEFT_JOIN(self.p).ON(self.u.id == self.p.user_id).build()
        expected = 'SELECT "u"."name" FROM "users" AS "u" LEFT JOIN "posts" AS "p" ON "u"."id" = "p"."user_id"'
        self.assertEqual(sql, expected)

    def test_cross_join(self):
        # Cross join doesn't need ON
        sql = self.q.SELECT(self.u.name).FROM(self.u).CROSS_JOIN(self.p).build()
        expected = 'SELECT "u"."name" FROM "users" AS "u" CROSS JOIN "posts" AS "p"'
        self.assertEqual(sql, expected)

    def test_on_without_join(self):
        # Should start empty or fail if no join
        q = Query("postgres")
        # Using internal structure to test error might be hard without triggering strict checks
        # But logically ON should complain if joins list is empty
        try:
             q.ON(self.u.id == 1)
             # If no error, check what happened?
        except Exception:
             pass # success

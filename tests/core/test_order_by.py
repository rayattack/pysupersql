from unittest import TestCase
from supersql import Query, Table

class TestOrderBy(TestCase):
    def setUp(self):
        self.q = Query("postgres")
        self.t = Table("posts").AS("p")

    def test_order_by_asc(self):
        sql = self.q.SELECT(self.t.id).FROM(self.t).ORDER_BY(self.t.id).build()
        self.assertIn('ORDER BY "p"."id" ASC', sql)

    def test_order_by_desc_unary(self):
        # This was failing
        sql = self.q.SELECT(self.t.id).FROM(self.t).ORDER_BY(-self.t.id).build()
        self.assertIn('ORDER BY "p"."id" DESC', sql)
        self.assertNotIn('ASC', sql.split('ORDER BY')[1])

    def test_order_by_multiple(self):
        sql = self.q.SELECT("*").FROM(self.t).ORDER_BY(self.t.id, -self.t.created_at).build()
        self.assertIn('ORDER BY "p"."id" ASC, "p"."created_at" DESC', sql)

    def test_order_by_string(self):
        sql = self.q.SELECT("*").FROM(self.t).ORDER_BY("id", "-created_at").build()
        self.assertIn('ORDER BY id ASC, created_at DESC', sql)

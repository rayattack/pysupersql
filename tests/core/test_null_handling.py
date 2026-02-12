from unittest import TestCase
from supersql import Query, Table

class TestNullHandling(TestCase):
    def setUp(self):
        self.q = Query("postgres")
        self.t = Table("users").AS("u")

    def test_eq_none(self):
        # t.field == None -> t.field IS NULL
        sql = self.q.SELECT("*").FROM(self.t).WHERE(self.t.name == None).build()
        self.assertIn('"u"."name" IS NULL', sql)
        self.assertNotIn('=', sql.split('WHERE')[1])

    def test_ne_none(self):
        # t.field != None -> t.field IS NOT NULL
        sql = self.q.SELECT("*").FROM(self.t).WHERE(self.t.name != None).build()
        self.assertIn('"u"."name" IS NOT NULL', sql)
        self.assertNotIn('<>', sql.split('WHERE')[1])

    def test_is_null_method(self):
        # t.field.IS_NULL() -> t.field IS NULL
        sql = self.q.SELECT("*").FROM(self.t).WHERE(self.t.name.IS_NULL()).build()
        self.assertIn('"u"."name" IS NULL', sql)

    def test_dynamic_none(self):
        # Simulating params.get('id') returning None
        val = None
        sql = self.q.SELECT("*").FROM(self.t).WHERE(self.t.id == val).build()
        self.assertIn('"u"."id" IS NULL', sql)

    def test_value_equality(self):
        # Normal value
        sql = self.q.SELECT("*").FROM(self.t).WHERE(self.t.name == "John").build()
        self.assertIn('"u"."name" = $1', sql)

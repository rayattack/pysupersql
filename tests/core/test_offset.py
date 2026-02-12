from unittest import TestCase
from supersql import Query, Table

class TestOffset(TestCase):
    def setUp(self):
        self.q = Query("postgres")
        self.t = Table("posts").AS("p")

    def test_offset_standalone(self):
        sql = self.q.SELECT("*").FROM(self.t).OFFSET(10).build()
        self.assertIn("OFFSET 10", sql)

    def test_limit_and_offset(self):
        sql = self.q.SELECT("*").FROM(self.t).LIMIT(5).OFFSET(10).build()
        self.assertIn("LIMIT 5", sql)
        self.assertIn("OFFSET 10", sql)

    def test_limit_with_offset_arg(self):
        # Existing behavior check
        sql = self.q.SELECT("*").FROM(self.t).LIMIT(5, offset=20).build()
        self.assertIn("LIMIT 5", sql)
        self.assertIn("OFFSET 20", sql)

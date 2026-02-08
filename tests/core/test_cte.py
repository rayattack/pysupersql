from unittest import TestCase
from supersql.core.query import Query
from supersql.core.state import QueryState

class TestCTE(TestCase):
    def setUp(self):
        self.q = Query('postgres', silent=True)

    def test_simple_cte(self):
        # WITH users_cte AS (SELECT * FROM users) SELECT * FROM users_cte
        
        q_cte = self.q._clone()
        q_cte = q_cte.SELECT('*').FROM('users')
        
        q_main = self.q._clone()
        q_main = q_main.WITH('users_cte', q_cte)
        q_main = q_main.SELECT('*').FROM('users_cte')
        
        expected = "WITH users_cte AS (SELECT * FROM users)\nSELECT * FROM users_cte"
        self.assertEqual(q_main.print(), expected)

    def test_multiple_ctes(self):
        # WITH cte1 AS (SELECT a FROM t1), cte2 AS (SELECT b FROM t2) SELECT * FROM cte1 JOIN cte2
        
        q1 = self.q._clone().SELECT('a').FROM('t1')
        q2 = self.q._clone().SELECT('b').FROM('t2')
        
        q_main = self.q._clone()
        q_main = q_main.WITH('cte1', q1).WITH('cte2', q2)
        q_main = q_main.SELECT('*').FROM('cte1').JOIN('cte2', on='cte1.a = cte2.b')
        
        # Note: Compiler joins CTEs with newline before main statement? 
        # Compiler logic: "\n".join(parts). parts = ["WITH ...", "SELECT ..."].
        expected = "WITH cte1 AS (SELECT a FROM t1), cte2 AS (SELECT b FROM t2)\nSELECT * FROM cte1 INNER JOIN cte2 ON cte1.a = cte2.b"
        self.assertEqual(q_main.print(), expected)
        
    def test_cte_with_string_subquery(self):
        # WITH old_users AS (SELECT * FROM users WHERE age > 50) DELETE FROM old_users
        
        # Test usage of string instead of Query object
        q_main = self.q._clone()
        q_main = q_main.WITH('old_users', "SELECT * FROM users WHERE age > 50")
        q_main = q_main.DELETE_FROM('old_users')
        
        expected = "WITH old_users AS (SELECT * FROM users WHERE age > 50)\nDELETE FROM old_users"
        self.assertEqual(q_main.print(), expected)

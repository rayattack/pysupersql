from unittest import TestCase
from supersql import Query, Table

class TestInsertConflict(TestCase):
    def setUp(self):
        self.q = Query("postgres")

    def test_insert_alias(self):
        """Test that INSERT works exactly like INSERT_INTO"""
        q1 = self.q.INSERT_INTO('users', ('name', 'age')).VALUES(('Alice', 30))
        q2 = self.q.INSERT('users', ('name', 'age')).VALUES(('Alice', 30))
        
        expected = 'INSERT INTO "users" ("name", "age") VALUES ($1, $2)'
        self.assertEqual(q1.print(), expected)
        self.assertEqual(q2.print(), expected)

    def test_on_conflict_do_nothing(self):
        """Test ON_CONFLICT ... DO_NOTHING"""
        q = self.q.INSERT('users', ('id', 'name')).VALUES((1, 'Alice'))
        q = q.ON_CONFLICT('id').DO_NOTHING()
        
        expected = 'INSERT INTO "users" ("id", "name") VALUES ($1, $2) ON CONFLICT (id) DO NOTHING'
        self.assertEqual(q.print(), expected)

    def test_on_conflict_do_update(self):
        """Test ON_CONFLICT ... DO_UPDATE"""
        q = self.q.INSERT('users', ('id', 'name')).VALUES((1, 'Alice'))
        q = q.ON_CONFLICT('id').DO_UPDATE(name='EXCLUDED.name')
        
        # Note: We implemented strict string handling in DO_UPDATE for now
        # kwargs are converted to "col" = val (quoted if str unless EXCLUDED)
        expected = 'INSERT INTO "users" ("id", "name") VALUES ($1, $2) ON CONFLICT (id) DO UPDATE SET "name" = EXCLUDED.name'
        self.assertEqual(q.print(), expected)

    def test_on_conflict_do_update_literal(self):
        """Test ON_CONFLICT ... DO_UPDATE with literal"""
        q = self.q.INSERT('users', ('id', 'name')).VALUES((1, 'Alice'))
        q = q.ON_CONFLICT('id').DO_UPDATE(name='Bob', attempts=0)
        
        # Order of kwargs matters in python 3.7+ (insertion order)
        # Checking if 'Bob' is quoted and 0 is literal
        expected = 'INSERT INTO "users" ("id", "name") VALUES ($1, $2) ON CONFLICT (id) DO UPDATE SET "name" = \'Bob\', "attempts" = 0'
        self.assertEqual(q.print(), expected)

    def test_on_conflict_multiple_targets(self):
        """Test ON_CONFLICT with multiple target columns"""
        q = self.q.INSERT('users', ('id', 'email')).VALUES((1, 'a@b.com'))
        q = q.ON_CONFLICT('id', 'email').DO_NOTHING()
        
        expected = 'INSERT INTO "users" ("id", "email") VALUES ($1, $2) ON CONFLICT (id, email) DO NOTHING'
        self.assertEqual(q.print(), expected)

    def test_returning_with_conflict(self):
        """Test RETURNING with ON CONFLICT"""
        q = self.q.INSERT('users', ('id',)).VALUES((1,))
        q = q.ON_CONFLICT('id').DO_NOTHING().RETURNING('*')
        
        expected = 'INSERT INTO "users" ("id") VALUES ($1) ON CONFLICT (id) DO NOTHING RETURNING *'
        self.assertEqual(q.print(), expected)

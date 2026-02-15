from unittest import TestCase
from supersql import Query, Table

class TestInsertQualification(TestCase):
    def setUp(self):
        self.q = Query("postgres")
        self.t = Table("users")

    def test_insert_field_objects_unqualified(self):
        """Test that Field objects passed to INSERT are not qualified with table name"""
        q = self.q.INSERT_INTO(self.t, (self.t.name, self.t.age)).VALUES(('Alice', 30))
        
        # Expectation: "name", "age" NOT "users"."name", "users"."age"
        expected = 'INSERT INTO "users" ("name", "age") VALUES ($1, $2)'
        self.assertEqual(q.print(), expected)

    def test_insert_aliased_table_fields(self):
        """Test that even with aliased tables based fields, columns are unqualified in INSERT"""
        # t alias u
        u = self.t.AS('u')
        
        q = self.q.INSERT_INTO(u, (u.name, u.age)).VALUES(('Bob', 25))
        
        # Expectation: INSERT INTO "users" ("name", "age") ... 
        # (Table name in INSERT INTO depends on how table handles it, usually it uses real name or alias?)
        # Standard SQL: INSERT INTO table (col)
        # If we use alias in INSERT INTO... `INSERT INTO users AS u` is valid in some DBs but not all.
        # But `supersql` `INSERT_INTO` logic:
        # if isinstance(table, Table): t = table.__tn__()
        # Table.__tn__() uses schema/name. It does NOT include AS alias usually?
        # Let's check Table.__tn__() implementation in previous turn (view_file of table.py).
        # __tn__ returns schema.name or name.
        # So it won't be aliased in the INSERT INTO clause, which is correct for standard SQL.
        # Columns should be unqualified "name", "age".
        
        expected = 'INSERT INTO "users" ("name", "age") VALUES ($1, $2)'
        self.assertEqual(q.print(), expected)

    def test_insert_mixed_string_and_fields(self):
        """Test mixing strings and Field objects"""
        q = self.q.INSERT_INTO(self.t, ('id', self.t.email)).VALUES((1, 'a@b.com'))
        
        expected = 'INSERT INTO "users" ("id", "email") VALUES ($1, $2)'
        self.assertEqual(q.print(), expected)

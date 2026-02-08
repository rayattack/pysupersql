from unittest import TestCase
from supersql.core.table import Table, Field

class T(TestCase):
    def test_instantiation(self):
        # Test basic instantiation
        t = Table('users')
        self.assertEqual(str(t), '"users"')
        
        # Test with schema
        t2 = Table('users', schema='public')
        self.assertEqual(str(t2), '"public"."users"')
        
        # Test with alias
        t3 = Table('users', alias='u')
        self.assertEqual(str(t3), '"users" AS "u"')
        
    def test_dynamic_fields(self):
        t = Table('users')
        f = t.name
        self.assertIsInstance(f, Field)
        self.assertEqual(str(f), '"users"."name"')
        
        # Test chaining
        t_alias = t.AS('u')
        f_alias = t_alias.name
        # Should use alias
        self.assertEqual(str(f_alias), '"u"."name"')
    
    def test_schema_fields(self):
        t = Table('users', schema='public')
        f = t.email
        # Should be "public"."users"."email" ? 
        # Check implementation of Field.__str__
        # It uses alias or name.
        # If no alias, use name.
        # "users"."email"
        # Wait, if schema is present, do we want fully qualified field names?
        # Standard SQL usually accepts table.field or alias.field.
        # It doesn't strictly need schema.table.field unless ambiguous, but it's valid.
        # My implementation of Field.__str__ was:
        # t_name = self.table._alias or self.table._name
        # return f'"{t_name}"."{self.name}"'
        # So it returns "users"."email".
        self.assertEqual(str(f), '"users"."email"')

    def test_operators(self):
        t = Table('users')
        f = t.age
        
        # Eq
        self.assertEqual(str(f == 5), '"users"."age" = 5')
        self.assertEqual(str(f == 'five'), '"users"."age" = \'five\'')
        
        # Gt
        self.assertEqual(str(f > 10), '"users"."age" > 10')
        
        # IN
        self.assertEqual(str(f.IN([1, 2, 3])), '"users"."age" IN (1, 2, 3)')

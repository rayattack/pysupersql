from supersql import Query
import pytest

def test_select_distinct_single_column():
    q = Query('sqlite', 'sqlite://jax.db')
    query = q.SELECT_DISTINCT('name').FROM('users')
    assert query.build() == 'SELECT DISTINCT name FROM "users"'

def test_select_distinct_multiple_columns():
    q = Query('sqlite', 'sqlite://jax.db')
    query = q.SELECT_DISTINCT('name', 'age').FROM('users')
    assert query.build() == 'SELECT DISTINCT name, age FROM "users"'

def test_select_distinct_star():
    q = Query('sqlite', 'sqlite://jax.db')
    query = q.SELECT_DISTINCT().FROM('users')
    assert query.build() == 'SELECT DISTINCT * FROM "users"'

def test_select_distinct_with_where():
    q = Query('sqlite', 'sqlite://jax.db')
    query = q.SELECT_DISTINCT('name').FROM('users').WHERE("age > 18")
    assert query.build() == 'SELECT DISTINCT name FROM "users" WHERE age > 18'

def test_select_distinct_with_order_by():
    q = Query('sqlite', 'sqlite://jax.db')
    query = q.SELECT_DISTINCT('name').FROM('users').ORDER_BY('name')
    assert query.build() == 'SELECT DISTINCT name FROM "users" ORDER BY name ASC'

def test_select_distinct_postgres():
    q = Query('postgres', 'postgres://u:p@h:5432/d')
    query = q.SELECT_DISTINCT('name').FROM('users')
    assert query.build() == 'SELECT DISTINCT name FROM "users"'

def test_select_distinct_mysql():
    q = Query('mysql', 'mysql://u:p@h:3306/d')
    query = q.SELECT_DISTINCT('name').FROM('users')
    assert query.build() == 'SELECT DISTINCT name FROM "users"'

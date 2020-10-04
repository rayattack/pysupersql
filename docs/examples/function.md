
```py



from suerpsql import Query, Schema, String


class Department(Schema):
    __tablename__ = 'deaprtments'
    name = String(25)


query = Query(
    vendor="postgres",
    host="localhost:5432",
    port=5432,
    user="postgres",
    password="postgres:user:password"
)

expected_sql = """
CREATE FUNCTION get_department(text) RETURNS departments
    AS $$ SELECT * FROM departments WHERE name = $1m $$
    LANGUAGE SQL;
"""

department = Department()
tablename = "tablename" or department

query.FUNCTION(
    "my_function_name"
).AS(
    query.SELECT().FROM(
        department
    ).WHERE(
        department.name == "$1"
    )
).LANGUAGE(
    "SQL IMMUTABLE STRICT"
) #This will actually work as it just translates your code to SQL and executes


another_expected_sql = """

CREATE FUNCTION concat_lower_or_upper(a text, b text, uppercase boolean DEFAULT false)
    AS
    $$
        SELECT CASE
            WHEN $3 THEN
                UPPER($1 || ' ' || $2)
            ELSE
                LOWER($1 || ' ' || $2)
            END;
    $$
    LANGUAGE SQL IMMUTABLE STRICT;
"""

concat_lower_or_upper = query.FUNCTION(
    "concat_lower_or_upper"
).AS(
    query.SELECT(
        department.name,
        query.CASE(
            query.WHEN(department.name == 1).THEN(

            )
        )
    )
)



```
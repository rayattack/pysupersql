from supersql import Query

from examples import config
from examples.schemas.employee import emp


q = Query(**config)

EMPS = (
    (1, 'Michael North', NULL),
    (2, 'Megan Berry', 1),
    (3, 'Sarah Berry', 1),
    (4, 'Zoe Black', 1),
    (5, 'Tim James', 1),
    (6, 'Bella Tucker', 2),
    (7, 'Ryan Metcalfe', 2),
    (8, 'Max Mills', 2),
    (9, 'Benjamin Glover', 2),
    (10, 'Carolyn Henderson', 3),
    (11, 'Nicola Kelly', 3),
    (12, 'Alexandra Climo', 3),
    (13, 'Dominic King', 3),
    (14, 'Leonard Gray', 4),
    (15, 'Eric Rampling', 4),
    (16, 'Piers Paige', 7),
    (17, 'Ryan Henderson', 7),
    (18, 'Frank Tucker', 8),
    (19, 'Nathan Ferguson', 8),
    (20, 'Kevin Rampling', 8)
)

populator = q.INSERT(emp).VALUES(
    EMPS
)


with_recursive = q.WITH_RECURSIVE("subordinates").AS(
    q.SELECT(
        emp.employee_id,
        emp.manager_id,
        emp.full_name
    ).FROM(emp).WHERE(
        emp.manager_id == None
    ).UNION(
        q.SELECT(
            emp.employee_id,
            emp.manager_id,
            emp.full_name
        ).FROM(
            emp
        ).JOIN(
            q.subordinates
        ).ON(q.subordinates.employee_id == emp.manager_id)
    )
)

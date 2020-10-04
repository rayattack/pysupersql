
```py

"""

.rows() -> iterator

.row(0)

.to_dataframe() -> Throw error if pandas not found
"""
from supersql import Query
from supersql import Results, Row

from examples import config
from examples.tables.actor import Actor



actor = """
actor_id    first_name      last_name       last_update
----------|---------------|---------------|-------------------------|
1           PENELOPE        GUINESS         2017-02-15 09:34:33+01
2           NICK            WAHLBERG        2017-02-15 09:34:33+01
3           ED              CHASE           2017-02-15 09:34:33+01
4           JENNIFER        DAVIS           2017-02-15 09:34:33+01
5           JOHNNY          LOLLOBRIGIDA    2017-02-15 09:34:33+01
"""


q = Query(**config)
actor = Actor()


results = q.SELECT().FROM(actor).execute()


# Get a list of all column headers
results.columns  # -> ['actor_id', 'first_name', 'last_name', 'last_update']


# Cells are the intersection between columns and rows
# e.g. 'LOLLOBRIGIDA' is cell(5,3) i.e. 5th Row, 3rd Column
#
# Every nested list is a row so (5, 3) is 5th list/row, 3rd item/column
# [
#     [1, 'boy', 'apple'],
#     [2, 'door', 'gun'],
#     [3, 'echo', 'mountain'],
#     [4, 'shark', 'adidas'],
#     [5, 'air', 'song']
# ]
#
lollobrigida = results.cell(5, 3)
print(lollobrigida)  # -> 'lollobrigida'


# To get all values in a col e.g. all first_names ['PENELOPE', 'NICK', 'ED', 'JENNIFER', 'JOHNNY']
# simply call column and pass in the name or number of the column
first_names = results.column('first_name')
first_names_again = results.column(2)
actor_ids = results.column('actor_id')



# To get a single row i.e. entire data on JOHNNY LOLLOBRIGIDA
johnny_lollobrigida = results.row(5)

# Now you can go crazy with Johnny
first_name = johnny_lollobrigida.first_name
last_name = johnny_lollobrigida.last_name
last_updated = johnny_lollobrigida.last_update


# Why not enable client side search? Because that should be the JOB of SQL and you
# should write a query that returns just what you want
# i.e.
# Most times you will get a single row or rows already sorted by how you want
# so you can get data easily
# remember - first position is for column which can be string or number, and second is for row (only numbers)
results.cell(5, 3)
results.column(3, 'first_name')
results.row(0)


# Want to iterate over all results
for data in results.rows():
    print(data.first_name)
    print(data.last_name)
    # etc


# Special Utility Methods
csvfile = results.to_csv(delimiter=',')  # Save to csv file - other options '\t', 
dataframe = results.to_dataframe()  # to pandas dataframe - raise error if pandas not installed
jsondata = results.to_dict()  # converts result set to python dict always nested in a list - [{}] or [{}, {}, {}]
jsonstring = results.to_json()  # string json representation - uses json.dumps(results.to_dict())


```
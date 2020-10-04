SuperSQL strives to make it as simple as possible to work with the data returned to you after
execution of your queries. To do this it provides two objects

- A result object that is an instance of the __[supersql.core.result.Result]()__ class
- And a Row object that is an instance of the __[supersql.core.row.Row]()__ class


### Results
Results are what is returned after executing a query and are a collection of 1 or more `Row`
objects.

For instance given the sql command below that returns the table immediately following it.

##### RAW SQL
```sql
SELECT * FROM employee ORDER BY first_name DESC LIMIT 2
```

##### Python (SuperSQL)
```py

query.SELECT().FROM(emp).ORDER_BY(-emp.first_name).LIMIT(2).execute()
```

| first_name        | last_name        | email                | age |
| ----------------- | :--------------: | :------------------: | ---:|
| John              | Doe              | john.doe@example.org | 34  |
| Jane              | Doe              | jane.doe@example.org | 30  |


will produce a Results Collection with 2 `supersql.core.row.Row` objects

A row here will be a single customer from the total results set (2 customers) that was
returned from the database engine.

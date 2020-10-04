
```py
from supersql import Query

q = Query(
    vendor="postgres",
    user="postgres",
    password="postgres",
    server="localhost:5432",
)

# or

q = Query(
    user="postgres",
    password="password",
    server="postgresql:=localhost:5432/mydatabase"
)

# or
q = Query("postgresql:=localhost:5432/mydatabase(username:=password)")

# You can also change the gopher delimiter
# to whatever you want
q = Query("postgresql:::localhost/mydatabase(username:::mypassword)", esc=":::")


host = "postgresql:=localhost:5432/mydatabase"
prompt_for_password = Query(user="postgres", prompt_password=True, host=host)
```

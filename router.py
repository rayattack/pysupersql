# installed libs
from routerling import Router, HttpRequest, ResponseWriter, Context
from ujson import dumps, loads

# internal modules
from supersql import Query, Table, String


query = Query('postgres', user="postgres", password="eldorad0", database="postgres")
router = Router()


class Customer(Table):
    name = String()


async def initialize(r, w, c):
    results = await query.sql("""
        BEGIN;

        CREATE TABLE otherworldly (
            email varchar(75) PRIMARY KEY NOT NULL,
            description text
        );

        COMMIT;
    """)
    w.body = results

async def selector(r, w, c):
    customer = Customer()
    results = await query.SELECT().FROM('customers').WHERE(customer.name == 'Kiki').run()
    if not (bool(results)): w.status = 404; return
    row = results.row(1)
    print(len(results._rows))
    w.body = f"{row.column('name')}, {row.title}"

async def editor(r: HttpRequest, w: ResponseWriter, c: Context):
    jsondata = loads(r.body)
    q = query.UPDATE('customers').SET(f"title = '{jsondata.get('title')}'").WHERE("name = 'Kiki'").RETURNING()
    results = await q.run()
    w.body = str(results)


async def creator(r: HttpRequest, w: ResponseWriter, c: Context):
    jsondata = loads(r.body)
    results = await query.INSERT_INTO('customers', ('name', 'title',)).VALUES(jsondata.values()).RETURNING().run() # () = ('*')
    w.body = str(results)


router.GET('/v1/customers', selector)
router.PUT('/v1/customers', editor)
router.POST('/v1/customers', creator)
router.POST('/v1/deletesss', initialize)

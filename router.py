from routerling import Router, HttpRequest, ResponseWriter, Context

from ujson import dumps, loads
from supersql import Query


query = Query('postgres', user="postgres", password="eldorad0", database="supersql")
router = Router()


async def selector(r, w, c):
    results = await query.SELECT().FROM('customers').WHERE("name = 'Kiki'").run()
    row = results.row(1)
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


```py

from supersql import Double
from supersql import Query, Table


query = Query(...)
f = query.FUNCTION()


DAYS = range(1,15)
MONTHS = ("November", "December", "January")
YEARS = (2019, 2018, 2017, 2016, 2015)
REGEXPR = "[a-zA-Z0-9]{{3}}-[a-zA-Z0-9]{{3}}-[a-zA-Z0-9]{{4}}-\\d{{2}}-[a-zA-Z0-9]{{4}}"


table = Table()
beetable = Table()
sskutable = Table()


CASE_REGEXP_LIKE = query.CASE(
    f.regexp_like(table.product_sku, REGEXPR)
).WHEN().THEN(
    f.substring(table.product_sku, 1, 15)
).ELSE(
    f.substring(table.product_sku, 1, 13)
).END()  # You can leave out END() as it is optional


CASE_COUNTRY_IN = query.CASE().WHEN(
    table.country.IN('DACH')
).THEN(
    f.upper(table.country)
)


with_aka_cte = query.WITH("cte_name").AS(
    query.SELECT(
        CASE_REGEXP_LIKE,
        f.replace(f.trim(f.lower('retailer_name'))).AS("retailer_name"),
        CASE_COUNTRY_IN,
        f.concat(table.year, table.month, table.day).AS("temp_day"),
        f.substr(f.min(table.crawl_date)).AS("found"),
        f.max(table.competitor_product_sku).AS("identifier"),
        f.round(f.sum(table.size_availability_score), 2).AS("size_availability_score"),
        f.avg(f.cast( table.retailer_sale_price.AS(Double) )).AS("current_price"),
        f.min(table.matching_date).AS("matching_date"),
        f.max(f.cast(table.retailer_sale_price.AS(Double))).AS("max_current_price"),
        f.max(f.cast(table.retailer_price.AS(Double))).AS("max_original_price"),
        f.max(table.offer_link).AS("product_url")
    ).FROM(
        table
    ).LEFT_JOIN(
        sskutable
    ).ON(
        sskutable.simple_sku == table.product_sku
    ).WHERE(
        table.year.IN(YEARS)
    ).AND(
        table.month.IN(MONTHS)
    ).AND(
        table.day.IN(DAYS)
    ).GROUP_BY(1, 2, 3, 4)
)

price_cte = query.WITH("price_data").AS(
    query.SELECT(
        CASE_REGEXP_LIKE,
        f.replace(f.trim(f.lower(table.retailer_name))).AS("retailer_name"),
        CASE_COUNTRY_IN,
        f.concat(table.year, table.month, table.day).AS("temp_day"),  # repetitive code can be put in a python function
        f.coalesce(
            f.max_by(f.cast(table.retailer_price.AS(Double)), table.size_availability_score),
            f.min(f.cast(table.retailer_sale_price).AS(Double))
        ).AS("retailer_sale_price")
    ).FROM(
        table
    ).LEFT_JOIN(
        sskutable
    ).ON(
        table.product_sku == sskutable.simple_sku
    ).WHERE(
        table.year.IN(YEARS)
    ).AND(
        table.month.IN(MONTHS)
    ).AND(
        table.days.IN(DAYS)
    ).GROUP_BY(1, 2, 3, 4)
)

query.SELECT(
    with_aka_cte.matched_csku.AS("matched_sku"),
    with_aka_cte.matched_csku.AS(" matched_csku"),
    with_aka_cte.retailer_name.AS(" retailer_name"),
    with_aka_cte.country_code.AS(" country_code"),
    f.max_by(with_aka_cte.found, with_aka_cte.temp_day).AS(" found"),
    f.max_by(with_aka_cte.identifier, with_aka_cte.temp_day).AS(" identifier"),
    f.max_by(with_aka_cte.size_availability_score, with_aka_cte.temp_day).AS(" size_availability_score"),
    f.max_by(with_aka_cte.current_price, with_aka_cte.temp_day).AS(" current_price"),
    f.max_by(with_aka_cte.matching_date, with_aka_cte.temp_day).AS(" matching_date"),
    f.max_by(with_aka_cte.max_current_price, with_aka_cte.temp_day).AS(" max_current_price"),
    f.max_by(with_aka_cte.max_original_price, with_aka_cte.temp_day).AS(" max_original_price"),
    f.max_by(price_cte.retailer_price, with_aka_cte.temp_day).AS(" retailer_price"),
    f.max_by(price_cte.retailer_sale_price, with_aka_cte.temp_day).AS(" retailer_sale_price"),
    f.max_by(with_aka_cte.product_url, with_aka_cte.temp_day).AS("product_url")
).FROM(
    price_cte
).JOIN(
    with_aka_cte
).ON(
    with_aka_cte.matched_csku == price_cte.matched_csku
).AND(
    with_aka_cte.retailer_name == price_cte.retailer_name
).AND(
    with_aka_cte.country_code == price_cte.country_code
).AND(
    with_aka_cte.temp_day == price_cte.temp_day
).GROUP_BY(1, 2, 3)


```
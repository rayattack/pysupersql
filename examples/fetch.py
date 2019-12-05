from supersql import Query

from .schemas.actor import Actor
from .schemas.staff import Staff


query = Query(
    user='postgres',
    password='postgres',
    vendor='postrgres',
    host='localhost:5432/mydatabase'
)
actor = Actor()

prep = query.SELECT(
    actor.actor_id,
    actor.first_name
).FROM(
    actor
).WHERE(
    actor.last_name == 'Connery'
).OFFSET(
    5
).FETCH(
    10
);


fetch_select = """

WITH 
cohort_data AS (
  SELECT sk_customer,
         iso_country_code country,
         FIRST(sk_order) OVER (PARTITION BY sk_customer ORDER BY order_date) sk_first_order,
         FIRST(order_date) OVER (PARTITION BY sk_customer ORDER BY order_date) first_order_date
  FROM f_salesorder_position sale
  LEFT JOIN d_shop shop
  ON sale.sk_shop = shop.sk_shop
  WHERE (sale.sk_order_date BETWEEN {cohort_start} AND {cohort_end}) AND
        sales_channel = 'SHOP'
),

cohort_data2 AS (
  SELECT sk_customer,
         sk_first_order,
         first_order_date,
         country
  FROM cohort_data
  GROUP BY 1,2,3,4
  ORDER BY COUNT(country) DESC
),

cohort AS (
  SELECT sk_customer,
         sk_first_order,
         first_order_date,
         FIRST(country) country
 FROM cohort_data2
 GROUP BY 1,2,3
),

shop_training AS (
  SELECT cohort.sk_customer,
         cohort.country,
         sk_order,
         first_order_date,
         (YEAR(order_date)-YEAR(first_order_date))*52 + WEEKOFYEAR(order_date) - WEEKOFYEAR(first_order_date) tt,
         (YEAR('{training_end_date}')-YEAR(first_order_date))*52 + WEEKOFYEAR('{training_end_date}') - WEEKOFYEAR(first_order_date) T,
         COALESCE(SUM(pcii),0) pcii
  FROM cohort
  LEFT JOIN f_salesorder_position sale
  ON cohort.sk_customer = sale.sk_customer
  LEFT JOIN d_shop shop
  ON sale.sk_shop = shop.sk_shop
  WHERE (sk_order_date BETWEEN {training_start} AND {training_end}) AND
        sales_channel = 'SHOP'
  GROUP BY 1,2,3,4,5,6
),

customer_stat AS (
  SELECT country,
         CAST(sk_customer AS int) sk_customer,
         CAST(first_order_date AS date) first_order_date,
         CAST(COUNT(*)-1 AS int) x,
         MAX(tt) tx,
         LEAST(MAX(T), {training_weeks_max}) T,
         SUM(pcii) pcii
  FROM shop_training
  WHERE tt <= {training_weeks_max}
  GROUP BY 1,2,3
),
result AS (
  SELECT *,
         row_number() OVER (PARTITION BY country ORDER BY RAND()) index
  FROM customer_stat
  WHERE x <= {training_n_basket_max} AND T >= {training_weeks_min}
)

SELECT country, sk_customer, x, tx, T, pcii
FROM result
WHERE index <= {training_n_customer}


"""

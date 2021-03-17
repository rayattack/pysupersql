
query += f"""
SELECT country,"""

for days in test_days_list:
query += f"""
P_alive_{days}d,
pcii_forecast_{days}d,
n_order_forecast_{days}d,
COALESCE(s{days}d.pcii_actual, 0) pcii_actual_{days}d,
CAST(COALESCE(s{days}d.n_order_actual, 0) AS DOUBLE) n_order_actual_{days}d,
CASE WHEN s{days}d.n_order_actual>0 THEN true ELSE false END is_alive_{days}d"""
query += """
FROM clv_inference ci"""
for days in test_days_list:
query += f"""
LEFT JOIN sales_{days}d s{days}d
ON ci.sk_customer = s{days}d.sk_customer"""

query += f"""
WHERE dt = {dt} AND run_id = '{run_id}'
"""

sql(query).createOrReplaceTempView("test_data")
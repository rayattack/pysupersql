from supersql import Schema
from supersql import (
    Double,
    Integer,
    String,
)


class cyberweek_competitive_data_raw(Schema):
    matched_config_sku = String()
    webshop_name = String()
    country_code = String()
    available = String()
    max_original_price = Integer()
    original_price = Integer()
    max_current_price = Double()
    current_price = Double()
    original_price = Double()
    current_price = Double()
    product_url = Double()
    last_seen = Double()
    currency_code = Double()

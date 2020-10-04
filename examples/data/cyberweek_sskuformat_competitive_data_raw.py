from datetime import datetime

from supersql import Schema
from supersql import (
    Date,
    Double,
    Integer,
    String,
)

class cyberweek_sskuformat_competitive_data_raw(Schema):
    matched_config_sku = String()
    matched_simple_sku = String()
    webshop_name = String()
    country_code = String()
    size_available = String()
    size_last_update = String(alias="found")
    size_identifier = String(alias="identifier")
    size_price_current = Integer(alias="current_price")
    current_date = Date(alias="matching_date", default=datetime.now, callback=datetime.now)  # both will produce the same output
    size_price_original = Integer()
    product_url = String()
    year = String()
    month = String()
    day = String()

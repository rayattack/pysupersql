from supersql.datatypes.base import Base
import json

class JSON(Base):
    """
    JSON datatype for storing lists, dicts, and objects.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def python_to_sql_value(self, value):
        if value is None:
            return 'NULL'
        if isinstance(value, (dict, list, tuple)):
            return f"'{json.dumps(value)}'"
        return f"'{str(value)}'"

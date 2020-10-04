

def get_tablename(string_identifier):
    """
    Irrespective of the type of naming convetion used i.e.
    3 part "schema.table.columnname" or 4 part "db.schema.table.columnname"
    this method expects the second part from the right to always be 
    table name
    """
    processed = string_identifier.split(".")
    parts = len(processed)
    if parts < 2:
        return processed[-1]
    else:
        return processed[-2]

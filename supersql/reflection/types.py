"""
Type mapping utilities for database reflection.

This module maps database-specific types to SuperSQL field types.
"""

from typing import Any, Optional, Union
from supersql.datatypes.string import String
from supersql.datatypes.numeric import Integer, Real, Decimal
from supersql.datatypes.boolean import Boolean
from supersql.datatypes.uuid import UUID
from supersql.datatypes.field import Field

# For now, use Field as base for date/time types until they're implemented
Date = Field
DateTime = Field
Time = Field
Float = Real  # Use Real instead of Float


def map_database_type_to_supersql(
    db_type: str, 
    nullable: bool = True, 
    default: Any = None,
    max_length: Optional[int] = None
) -> Any:
    """
    Map a database type to the corresponding SuperSQL field type.
    
    Args:
        db_type: Database-specific type string
        nullable: Whether the field allows NULL values
        default: Default value for the field
        max_length: Maximum length for string types
        
    Returns:
        SuperSQL field instance
    """
    db_type = db_type.lower()
    
    # PostgreSQL type mappings
    if 'varchar' in db_type or 'character varying' in db_type:
        length = _extract_length(db_type) or max_length
        return String(length=length, required=not nullable, default=default)
    
    elif 'char' in db_type and 'varchar' not in db_type:
        length = _extract_length(db_type) or max_length
        return String(length=length, required=not nullable, default=default)
    
    elif db_type in ('text', 'longtext', 'mediumtext'):
        return String(required=not nullable, default=default)
    
    elif db_type in ('integer', 'int', 'int4', 'serial'):
        return Integer(required=not nullable, default=default)
    
    elif db_type in ('bigint', 'int8', 'bigserial'):
        return Integer(required=not nullable, default=default)
    
    elif db_type in ('smallint', 'int2', 'smallserial'):
        return Integer(required=not nullable, default=default)
    
    elif db_type in ('real', 'float4'):
        return Float(required=not nullable, default=default)
    
    elif db_type in ('double precision', 'float8', 'float'):
        return Float(required=not nullable, default=default)
    
    elif 'decimal' in db_type or 'numeric' in db_type:
        return Decimal(required=not nullable, default=default)
    
    elif db_type in ('boolean', 'bool'):
        return Boolean(required=not nullable, default=default)
    
    elif db_type == 'uuid':
        return UUID(required=not nullable, default=default)
    
    elif db_type in ('date',):
        return Date(required=not nullable, default=default)
    
    elif db_type in ('timestamp', 'timestamp without time zone', 'timestamp with time zone', 'datetime'):
        return DateTime(required=not nullable, default=default)
    
    elif db_type in ('time', 'time without time zone', 'time with time zone'):
        return Time(required=not nullable, default=default)
    
    # MySQL specific types
    elif db_type in ('tinyint', 'mediumint'):
        return Integer(required=not nullable, default=default)
    
    elif db_type == 'year':
        return Integer(required=not nullable, default=default)
    
    elif 'enum' in db_type:
        return String(required=not nullable, default=default)
    
    elif db_type in ('json', 'jsonb'):
        return String(required=not nullable, default=default)  # Could be a JSON type in the future
    
    # SQLite specific types
    elif db_type in ('blob',):
        return String(required=not nullable, default=default)  # Could be a Binary type in the future
    
    # Default fallback
    else:
        # For unknown types, default to String
        return String(required=not nullable, default=default)


def _extract_length(type_string: str) -> Optional[int]:
    """
    Extract length from type string like 'varchar(255)'.
    
    Args:
        type_string: Database type string
        
    Returns:
        Length as integer or None if not found
    """
    import re
    
    match = re.search(r'\((\d+)\)', type_string)
    if match:
        return int(match.group(1))
    return None


# Type mapping dictionaries for different databases
POSTGRES_TYPE_MAP = {
    'varchar': String,
    'character varying': String,
    'char': String,
    'character': String,
    'text': String,
    'integer': Integer,
    'int': Integer,
    'int4': Integer,
    'bigint': Integer,
    'int8': Integer,
    'smallint': Integer,
    'int2': Integer,
    'serial': Integer,
    'bigserial': Integer,
    'smallserial': Integer,
    'real': Float,
    'float4': Float,
    'double precision': Float,
    'float8': Float,
    'numeric': Decimal,
    'decimal': Decimal,
    'boolean': Boolean,
    'bool': Boolean,
    'uuid': UUID,
    'date': Date,
    'timestamp': DateTime,
    'timestamp without time zone': DateTime,
    'timestamp with time zone': DateTime,
    'time': Time,
    'time without time zone': Time,
    'time with time zone': Time,
    'json': String,
    'jsonb': String,
}

MYSQL_TYPE_MAP = {
    'varchar': String,
    'char': String,
    'text': String,
    'longtext': String,
    'mediumtext': String,
    'tinytext': String,
    'int': Integer,
    'integer': Integer,
    'bigint': Integer,
    'smallint': Integer,
    'mediumint': Integer,
    'tinyint': Integer,
    'float': Float,
    'double': Float,
    'decimal': Decimal,
    'numeric': Decimal,
    'boolean': Boolean,
    'bool': Boolean,
    'date': Date,
    'datetime': DateTime,
    'timestamp': DateTime,
    'time': Time,
    'year': Integer,
    'json': String,
    'enum': String,
    'set': String,
}

SQLITE_TYPE_MAP = {
    'text': String,
    'varchar': String,
    'char': String,
    'integer': Integer,
    'int': Integer,
    'real': Float,
    'numeric': Decimal,
    'boolean': Boolean,
    'date': Date,
    'datetime': DateTime,
    'timestamp': DateTime,
    'time': Time,
    'blob': String,  # Could be Binary in the future
}

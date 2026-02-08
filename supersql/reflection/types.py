"""
Type mapping utilities for database reflection.

This module maps database-specific types to SuperSQL field types.
"""

from typing import Any, Optional
from supersql.core.table import Field

# Define lightweight types for reflection results
class ReflectedType(Field):
    def __init__(self, required: bool = True, default: Any = None, length: Optional[int] = None):
        self.required = required
        self.default = default
        self.length = length

class String(ReflectedType): pass
class Integer(ReflectedType): pass
class Real(ReflectedType): pass
class Decimal(ReflectedType): pass
class Boolean(ReflectedType): pass
class UUID(ReflectedType): pass
class Date(ReflectedType): pass
class DateTime(ReflectedType): pass
class Time(ReflectedType): pass
class Float(ReflectedType): pass


def map_database_type_to_supersql(
    db_type: str, 
    nullable: bool = True, 
    default: Any = None,
    max_length: Optional[int] = None
) -> Any:
    """
    Map a database type to the corresponding SuperSQL field type.
    """
    db_type = db_type.lower()
    
    if 'int' in db_type or 'serial' in db_type:
        return Integer(required=not nullable, default=default)
    elif 'char' in db_type or 'text' in db_type or 'enum' in db_type or 'json' in db_type:
        return String(required=not nullable, default=default, length=max_length)
    elif 'bool' in db_type:
        return Boolean(required=not nullable, default=default)
    elif 'uuid' in db_type:
        return UUID(required=not nullable, default=default)
    elif 'date' in db_type or 'time' in db_type:
        return DateTime(required=not nullable, default=default)
    elif 'float' in db_type or 'double' in db_type or 'decimal' in db_type or 'numeric' in db_type:
        return Float(required=not nullable, default=default)
    
    return String(required=not nullable, default=default)

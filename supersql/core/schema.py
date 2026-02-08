from typing import TypedDict, Annotated, Type, Dict, Any, get_type_hints
from supersql.datatypes.numeric import Integer, Double, Number
from supersql.datatypes.base import Base
from supersql.datatypes.string import String, Char, Text
from supersql.core.table import Table

# Initialize global validator from Pytastic if needed, or rely on internal validation
from pytastic import Pytastic
_vx = Pytastic()

class SchemaMeta(type):
    """
    Metaclass to convert Pytastic Annotated types into SuperSQL descriptors.
    """
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        
        if name == 'Schema':
            return cls

        # Get type hints
        try:
            hints = get_type_hints(cls, include_extras=True)
        except Exception:
            hints = cls.__annotations__ if hasattr(cls, '__annotations__') else {}

        fields_cache = {}

        for field_name, annotation in hints.items():
            descriptor = mcs._create_descriptor(field_name, annotation)
            if descriptor:
                setattr(cls, field_name, descriptor)
                if hasattr(descriptor, '__set_name__'):
                    descriptor.__set_name__(cls, field_name)
                
                fields_cache[field_name] = descriptor

        cls.fields_cache = fields_cache
        # Register for validation
        try:
            _vx.register(cls)
        except Exception:
            pass # Maybe already registered or partial class

        return cls

    @staticmethod
    def _create_descriptor(name: str, annotation: Any) -> Base:
        # Unwrap Annotated
        if hasattr(annotation, '__metadata__') and annotation.__metadata__:
             constraints = [m for m in annotation.__metadata__ if isinstance(m, str)]
             constraint_str = ";".join(constraints)
             base_type = annotation.__origin__
        else:
            base_type = annotation
            constraint_str = ""
        
        # Parse logic
        kwargs = SchemaMeta._parse_constraints(constraint_str)
        
        # Type Mapping
        if base_type is int:
            return Integer(**kwargs)
        elif base_type is float:
            return Double(**kwargs)
        elif base_type is str:
            # Check for specific formats or length to decide String vs Text vs Char
            # For now default to String (VARCHAR)
            return String(**kwargs)
        
        return None

    @staticmethod
    def _parse_constraints(constraint_str: str) -> Dict[str, Any]:
        """
        Parse 'min=1; max=10' into {'minimum': 1, 'maximum': 10}
        """
        kwargs = {}
        if not constraint_str:
            return kwargs
            
        rules = constraint_str.split(';')
        for rule in rules:
            rule = rule.strip()
            if not rule: continue
            
            key, value = rule, True
            if '=' in rule:
                key, value = rule.split('=', 1)
            
            key = key.strip()
            if isinstance(value, str):
                value = value.strip()
                if value.isdigit(): value = int(value)
                elif value.replace('.', '', 1).isdigit(): value = float(value)
                elif value.lower() == 'true': value = True
                elif value.lower() == 'false': value = False
                
            # Mapping Pytastic -> SuperSQL
            if key == 'min': kwargs['minimum'] = value
            elif key == 'max': kwargs['maximum'] = value
            elif key == 'min_len': kwargs['min_length'] = value 
            elif key == 'max_len': kwargs['max_length'] = value
            elif key == 'required': kwargs['required'] = value
            elif key == 'unique': kwargs['unique'] = value
            elif key == 'primary_key': kwargs['pk'] = value # Pytastic doesn't have pk usually, but for supersql
            
        return kwargs

class Schema(dict, metaclass=SchemaMeta):
    """
    Base class for Pytastic-powered SuperSQL schemas.
    """
    __tablename__ = None
    
    @classmethod
    def __tn__(cls):
        return cls.__tablename__.lower() if cls.__tablename__ else cls.__name__.lower()
        
    @classmethod
    def columns(cls):
        # Return descriptors
        return list(cls.fields_cache.values())
        
    def validate(self):
        _vx.validate(self.__class__, self)


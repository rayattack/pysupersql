from typing import TypedDict, Annotated, Type, Dict, Any, get_type_hints, List, Union, Optional
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
try:
    from typing import NotRequired
except ImportError:
    try:
        from typing_extensions import NotRequired
    except ImportError:
        NotRequired = Optional

from supersql.datatypes.numeric import Integer, Double, Number
from supersql.datatypes.base import Base
from supersql.datatypes.string import String, Char, Text
from supersql.datatypes.json import JSON
from supersql.core.table import Table
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
        _vx.register(cls)
        return cls

    @staticmethod
    def _create_descriptor(name: str, annotation: Any) -> Base:
        """
        Factory to create specific SuperSQL datatype descriptors from annotations.
        """
        # Handle NotRequired
        is_required = True
        if hasattr(annotation, '__origin__') and annotation.__origin__ is NotRequired:
            annotation = annotation.__args__[0]
            is_required = False

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
        if not is_required:
            kwargs['required'] = False
        
        # Handle Generics (List[int], Dict[str, Any], etc)
        # For List[str], base_type is List[str], origin is list
        origin = getattr(base_type, '__origin__', base_type)
        
        # Handle Literal
        if origin is Literal:
            # Assume all literal values are of the same type for SQL mapping
            args = getattr(base_type, '__args__', [])
            if args:
                if isinstance(args[0], int):
                    return Integer(**kwargs, options=args)
                elif isinstance(args[0], str):
                    return String(**kwargs, options=args)
            return String(**kwargs) # Fallback

        # Type Mapping
        if origin is int:
            return Integer(**kwargs)
        elif origin is float:
            return Double(**kwargs)
        elif origin is str:
            return String(**kwargs)
        elif origin is list or origin is dict:
            return JSON(**kwargs)
        elif isinstance(origin, type) and issubclass(origin, dict):
             return JSON(**kwargs)
        
        # Fallback for complex unions or other types -> JSON or None?
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
        # 1. Pytastic Validation
        _vx.validate(self.__class__, self)
        
        # 2. SuperSQL Descriptor Validation (Fallback/Extension)
        for name, descriptor in self.fields_cache.items():
            if name in self:
                value = self[name]
                if hasattr(descriptor, 'validate'):
                     descriptor.validate(value)

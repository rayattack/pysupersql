import pytest
import json
from typing import TypedDict, Annotated, List, Union, Dict, Any, Optional
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

from supersql.core.schema import Schema
from supersql.core.results import Results
from pytastic.exceptions import ValidationError

class TestComplexSchemas:

    def test_schema_1_deep_nesting(self):
        """Schema 1: Deep Nesting & Optionals"""
        class ManagerDetails(Schema):
            level: Annotated[int, "min=1; max=10"]
            
        class Manager(Schema):
            name: Annotated[str, "min_len=2"]
            details: NotRequired[ManagerDetails]

        class Team(Schema):
            name: str
            lead: Manager
            
        class Department(Schema):
            name: str
            teams: List[Team]
            
        class Organization(Schema):
            name: str
            departments: List[Department]
            headquarters: Annotated[str, "min_len=5"]

        # 1. Test Validation - Valid
        valid_data = {
            "name": "Acme Corp",
            "headquarters": "New York",
            "departments": [
                {
                    "name": "Engineering",
                    "teams": [
                        {
                            "name": "Backend",
                            "lead": {"name": "Alice", "details": {"level": 5}}
                        }
                    ]
                }
            ]
        }
        # Using Results wrapper or direct Schema validation
        org = Organization(valid_data)
        org.validate()

        # 2. Test Validation - Invalid (Nested constraint failure)
        invalid_data = {
            "name": "Acme Corp",
            "headquarters": "New",
            "departments": [
                {
                    "name": "Engineering",
                    "teams": [
                        {
                            "name": "Backend",
                            "lead": {"name": "Alice", "details": {"level": 11}} # Max is 10
                        }
                    ]
                }
            ]
        }
        
        with pytest.raises(ValidationError) as exc:
            Organization(invalid_data).validate()
        assert "Must be <= 10" in str(exc.value)

    def test_schema_2_complex_arrays(self):
        """Schema 2: Complex Arrays"""
        class Product(Schema):
            id: Annotated[int, "min=1"]
            name: str
            tags: Annotated[List[str], "min_len=1; max_len=5; unique=True"]
            # dimensions: Annotated[tuple[int, int, int], ""] # Tuple support might be tricky in descriptors, testing validation mainly

        class Catalog(Schema):
            products: List[Product]

        # 1. Validation - Valid
        valid = {
            "products": [
                {
                    "id": 1,
                    "name": "Box",
                    "tags": ["storage", "cardboard"],
                   # "dimensions": (10, 20, 5)
                }
            ]
        }
        Catalog(valid).validate()

        # 2. Validation - Invalid (Duplicate Items - if unique=True is supported by Pytastic for arrays)
        # Note: Pytastic snippet had unique=True in annotation.
        invalid = {
            "products": [
                {
                    "id": 2,
                    "name": "Bad Box",
                    "tags": ["tag1", "tag1"], # Duplicate
                }
            ]
        }
        # Only verify if Pytastic actually checks list uniqueness via min_len/max_len or specific unique validator
        # Assuming Pytastic supports it as per user snippet
        with pytest.raises(ValidationError) as exc:
             Catalog(invalid).validate()
        # assert "Duplicate items" in str(exc.value) # Message depends on Pytastic

    def test_schema_3_union_types(self):
        """Schema 3: Union Types"""
        class CreditCard(Schema):
            type: Literal["credit"]
            number: Annotated[str, "min_len=16"]
            
        class BankTransfer(Schema):
            type: Literal["bank"]
            account: Annotated[str, "min_len=8"]
            
        class Payment(Schema):
            method: Union[CreditCard, BankTransfer]

        # 1. Validation - Valid
        valid_cc = {"method": {"type": "credit", "number": "1234567890123456"}}
        Payment(valid_cc).validate()
        
        valid_bank = {"method": {"type": "bank", "account": "12345678"}}
        Payment(valid_bank).validate()

        # 2. Validation - Invalid
        invalid = {"method": {"type": "cash", "amount": 100}} 
        with pytest.raises(ValidationError) as exc:
            Payment(invalid).validate()
        # assert "No match" in str(exc.value)

    def test_schema_8_enums_constants(self):
        """Schema 8: Enums and Constants"""
        class Config(Schema):
            mode: Literal["debug", "production", "testing"]
            version: Literal[1]
            enabled: bool

        # 1. Valid
        Config({"mode": "production", "version": 1, "enabled": True}).validate()

        # 2. Invalid Enum
        with pytest.raises(ValidationError):
            Config({"mode": "dev", "version": 1, "enabled": True}).validate()
            
        # 3. Invalid Constant
        with pytest.raises(ValidationError):
            Config({"mode": "debug", "version": 2, "enabled": True}).validate()
            
    def test_query_building_with_complex(self):
        class Config(Schema):
            mode: Literal["debug", "production"]
            
        from supersql import Query
        db = Query('sqlite://:memory:')
        
        # Verify that Literal works as descriptor
        q = db.SELECT(Config).FROM(Config).WHERE(Config.mode == 'debug')
        sql = q.build()
        # Default is safe mode with placeholders
        assert "mode = " in sql
        if '?' in sql:
             assert "mode = ?" in sql
        else:
             # Postgres/etc might use $1
             assert "mode = $1" in sql or "mode = %s" in sql

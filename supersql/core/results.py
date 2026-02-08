from typing import Any, List, Optional, Union, Iterator, AsyncIterator
# from supersql.core.schema import Schema # Circular import risk, use Any or specific type checking

class Result(object):
    def __init__(self, record: Any, schema: Any = None):
        self.__ = record
        self._schema = schema
        
        # Validate immediately if schema is present
        if self._schema:
            # We need to construct a schema instance from the record to validate it?
            # Or just validate the dict against the schema class?
            # Pytastic validate(SchemaClass, data)
            try:
                # If the schema class has a validate method that takes an instance, use it
                # But Pytastic is vx.validate(Type, data).
                # Assuming schema passed here is the Schema Class
                if hasattr(self._schema, 'validate'):
                     # This might be an instance method on Schema instances, 
                     # but we have a dict record.
                     # We should use the global validator or a method on the class
                     from pytastic import Pytastic
                     vx = Pytastic()
                     vx.validate(self._schema, self.__)
            except Exception as e:
                # Raise or log? For now raise to enforce schema
                raise e

    def column(self, col: str) -> Any:
        return self.__.get(col)
    
    def __getattr__(self, column: str) -> Any:
        try:
            return self.__.get(column)
        except AttributeError:
             # If strictly validated, maybe we should raise if not in schema?
             # For now fallback to None or AttributeError
             raise AttributeError(f"Result has no column '{column}'")

    def __getitem__(self, key: str) -> Any:
        return self.__.get(key)

    def __repr__(self):
        return f"<Result {self.__}>"


class Results(object):
    def __init__(self, records: Union[List[Any], Any], schema: Any = None):
        if not isinstance(records, list):
            # defined below, but python scoping allows this if class is defined in module
            records = [SingleValueRecord(records)]
        self._rows: List[Any] = records
        self._copy: List[Any] = records[:]
        self._schema = schema

    def cell(self, row: int, col: str) -> Any:
        row -= 1
        record = self._rows[row] 
        return record.get(col)

    def row(self, row: int) -> Result:
        row -= 1
        return Result(self._rows[row], schema=self._schema)
    
    def column(self, name: str, limit: Optional[int] = None) -> None:
        """Get all the values in this column and limit it to `limit` provided"""
        pass

    def rows(self, limit: Optional[int] = None) -> 'Results':
        return Results(self._rows[:limit], schema=self._schema)
    
    def seek(self, index: int = 0) -> None:
        self._copy = self._rows[index:]
    
    def __bool__(self) -> bool:
        return bool(self._rows)

    def __iter__(self) -> Iterator[Result]:
        return self

    def __next__(self) -> Result:
        if not self._copy:
            raise StopIteration
        return Result(self._copy.pop(0), schema=self._schema)

    def __aiter__(self) -> 'Results':
        return self

    async def __anext__(self) -> Result:
        if not self._copy:
            raise StopAsyncIteration
        return Result(self._copy.pop(0), schema=self._schema)


class SingleValueRecord(object):
    def __init__(self, record: Any):
        self._single_value_record = record
    
    def get(self, key: Any) -> Any:
        return self._single_value_record

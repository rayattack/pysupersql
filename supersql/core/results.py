from typing import Any, List, Optional, Union, Iterator, AsyncIterator


class Result(object):
    def __init__(self, record: Any, schema: Any = None):
        self.__ = record
        self._schema = schema

    def column(self, col: str) -> Any:
        return self.__.get(col)
    
    def __getattr__(self, column: str) -> Any:
        try: return self.__.get(column)
        except AttributeError:
             raise AttributeError(f"Result has no column '{column}'")

    def data(self) -> Any:
        return self.__

    def __getitem__(self, key: str) -> Any:
        return self.__.get(key)
    
    def __iter__(self):
        # Allow dict(result) to work
        return iter(self.__)

    def keys(self):
        return self.__.keys()

    def values(self):
        return self.__.values()

    def items(self):
        return self.__.items()

    def __repr__(self):
        return f"<Result {self.__}>"


class SingleValueRecord(object):
    def __init__(self, record: Any):
        self._single_value_record = record

    def get(self, key: Any) -> Any:
        return self._single_value_record


class Results(object):
    def __init__(self, records: Union[List[Any], Any], schema: Any = None):
        # defined below, but python scoping allows this if class is defined in module
        if not isinstance(records, list): records = [SingleValueRecord(records)]
        self._rows: List[Any] = records
        self._copy: List[Any] = records[:]
        self._schema = schema

    def first(self) -> Optional[Result]:
        """Returns the first Result object or None if empty."""
        if not self._rows: return None
        return Result(self._rows[0], schema=self._schema)

    def cell(self, row: Optional[int] = None, col: Optional[str] = None) -> Any:
        """
        Returns the value of the first cell (row 0, col 0) or None if no args provided.
        If row and col are provided, returns the value at that specific position (legacy).
        """
        if row is not None and col is not None:
             # Legacy behavior
             record = self._rows[row] 
             return record.get(col)

        if not self._rows: return None
        first_row = self._rows[0]

        # If it's a SingleValueRecord, return it directly
        if isinstance(first_row, SingleValueRecord):
            return first_row.get(None)
        # If it's a dict/Record, return the first value found
        if hasattr(first_row, 'values'):
             # This assumes order is preserved (Python 3.7+)
             return next(iter(first_row.values())) if first_row else None
        
        # Fallback: return the row itself (assuming it's a primitive value)
        return first_row

    def cells(self) -> List[Any]:
        """Returns a list of values from the first column of all rows."""
        vals = []
        for r in self._rows:
            if isinstance(r, SingleValueRecord):
                vals.append(r.get(None))
            elif hasattr(r, 'values'):
                vals.append(next(iter(r.values())) if r else None)
            else:
                # Primitive value
                vals.append(r)
        return vals

    def row(self, row: int) -> Result:
        row -= 1
        return Result(self._rows[row], schema=self._schema)
    
    def column(self, name: str) -> List[Any]:
        return [r.get(name) for r in self._rows]

    def data(self) -> List[Any]:
        return [r.get(None) if isinstance(r, SingleValueRecord) else r for r in self._rows]

    def rows(self, limit: Optional[int] = None) -> 'Results':
        if limit is None: return Results(self._rows, schema=self._schema)
        return Results(self._rows[:limit], schema=self._schema)
    
    def seek(self, index: int = 0) -> None:
        self._copy = self._rows[index:]
    
    def __bool__(self) -> bool:
        return bool(self._rows)

    def __iter__(self) -> Iterator[Result]:
        # Return a new iterator to avoid consuming the main copy/pointer
        return iter([Result(r, schema=self._schema) for r in self._rows])

    def __getitem__(self, index: int) -> Result:
        return Result(self._rows[index], schema=self._schema)

    def __next__(self) -> Result:
        if not self._copy: raise StopIteration
        return Result(self._copy.pop(0), schema=self._schema)

    def __aiter__(self) -> 'Results':
        return self

    async def __anext__(self) -> Result:
        if not self._copy: raise StopAsyncIteration
        return Result(self._copy.pop(0), schema=self._schema)

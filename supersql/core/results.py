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

    def __repr__(self):
        return f"<Result {self.__}>"


class Results(object):
    def __init__(self, records: Union[List[Any], Any], schema: Any = None):
        # defined below, but python scoping allows this if class is defined in module
        if not isinstance(records, list): records = [SingleValueRecord(records)]
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
    
    def column(self, name: str) -> List[Any]:
        return [r.get(name) for r in self._rows]

    def data(self) -> List[Any]:
        return [r.get(None) if isinstance(r, SingleValueRecord) else r for r in self._rows]

    def rows(self, limit: Optional[int] = None) -> 'Results':
        return Results(self._rows[:limit], schema=self._schema)
    
    def seek(self, index: int = 0) -> None:
        self._copy = self._rows[index:]
    
    def __bool__(self) -> bool:
        return bool(self._rows)

    def __iter__(self) -> Iterator[Result]:
        return self

    def __next__(self) -> Result:
        if not self._copy: raise StopIteration
        return Result(self._copy.pop(0), schema=self._schema)

    def __aiter__(self) -> 'Results':
        return self

    async def __anext__(self) -> Result:
        if not self._copy: raise StopAsyncIteration
        return Result(self._copy.pop(0), schema=self._schema)


class SingleValueRecord(object):
    def __init__(self, record: Any):
        self._single_value_record = record

    def get(self, key: Any) -> Any:
        return self._single_value_record

from typing import Any, List, Optional, Union, Iterator, AsyncIterator


class Result(object):
    def __init__(self, record: Any):
        self.__ = record

    def column(self, col: str) -> Any:
        return self.__.get(col)
    
    def __getattr__(self, column: str) -> Any:
        return self.__.get(column)


class Results(object):
    def __init__(self, records: Union[List[Any], Any]):
        if not isinstance(records, list):
            # defined below, but python scoping allows this if class is defined in module
            records = [SingleValueRecord(records)]
        self._rows: List[Any] = records
        self._copy: List[Any] = records[:]

    def cell(self, row: int, col: str) -> Any:
        row -= 1
        record = self._rows[row] 
        return record.get(col)

    def row(self, row: int) -> Result:
        row -= 1
        return Result(self._rows[row])
    
    def column(self, name: str, limit: Optional[int] = None) -> None:
        """Get all the values in this column and limit it to `limit` provided"""
        pass

    def rows(self, limit: Optional[int] = None) -> 'Results':
        return Results(self._rows[:limit])
    
    def seek(self, index: int = 0) -> None:
        self._copy = self._rows[index:]
    
    def __bool__(self) -> bool:
        return bool(self._rows)

    def __iter__(self) -> Iterator[Result]:
        return self

    def __next__(self) -> Result:
        if not self._copy:
            raise StopIteration
        return Result(self._copy.pop(0))

    def __aiter__(self) -> 'Results':
        return self

    async def __anext__(self) -> Result:
        if not self._copy:
            raise StopAsyncIteration
        return Result(self._copy.pop(0))


class SingleValueRecord(object):
    def __init__(self, record: Any):
        self._single_value_record = record
    
    def get(self, key: Any) -> Any:
        return self._single_value_record

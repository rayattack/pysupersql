from typing import Any


class Result(object):
    def __init__(self, record):
        self.__ = record

    def column(self, col: str):
        return self.__.get(col)
    
    def __getattr__(self, column):
        return self.__.get(column)


class Results(object):
    def __init__(self, records):
        if not isinstance(records, list):
            records = [SingleValueRecord(records)]
        self._rows = records
        self._copy = records[:]

    def cell(self, row: int, col: str) -> Any:
        row -= 1
        row = self._rows[row] # yes we overwrote the variable i.e converted it from num to a row
        return row.get(col)

    def row(self, row: int):
        row -= 1
        return Result(self._rows[row])
    
    def column(self, name: str, limit: int = None):
        """Get all the values in this column and limit it to `limit` provided"""
        pass

    def rows(self, limit: int = None):
        return Results(self._rows[:limit])
    
    def seek(self, index=0):
        self._copy = self._rows[index:]
    
    def __bool__(self):
        return bool(self._rows)

    def __iter__(self):
        return self

    def __next__(self):
        if not self._copy:
            raise StopIteration
        return Result(self._copy.pop(0))

    def __aiter__(self):
        return self

    def __anext__(self):
        if not self._copy:
            raise StopAsyncIteration
        yield Result(self._copy.pop())


class SingleValueRecord(object):
    def __init__(self, record):
        self._single_value_record = record
    
    def get(self, key):
        return self._single_value_record

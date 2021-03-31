from typing import TYPE_CHECKING
from typing import Any, List, Mapping

from abc import abstractmethod


class IEngine:
    @abstractmethod
    async def connect(self) -> None:...

    @abstractmethod
    async def disconnect(self) -> None:...

    @abstractmethod
    def connection(self) -> "Connection":...


class IConnection:
    @abstractmethod
    async def begin(self) -> None:...

    @abstractmethod
    async def done(self) -> None:...

    @abstractmethod
    async def execute(self, query: 'Query') -> Any:...

    @abstractmethod
    async def executemany(self, queries: List['Query']) -> Any:...

    @abstractmethod
    async def fetchall(self, query: "Query") -> List[Mapping]:...

    @abstractmethod
    async def fetchmany(self, limit: int) -> Any:...

    @abstractmethod
    async def release(self) -> None:...

    @abstractmethod
    async def rowcount(self, query: 'Query') -> int:...

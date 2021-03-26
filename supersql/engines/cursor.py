class Cursor:
    @property
    def description(self) -> str:
        raise NotImplementedError()

    @property
    def rowcount(self) -> int:
        raise NotImplementedError()

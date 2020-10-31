
from supersql.datatypes.base import Base


class UUID(Base):
    def __init__(self, *args, **kwargs):
        self.pk = kwargs.get("pk") or kwargs.get("primary_key")
        self.required = kwargs.get("required")
        self.default = kwargs.get("default")
        self.unique = kwargs.get("unique")
        self.textsearch = kwargs.get("textsearch")
        self.options = kwargs.get("options")

        self.uuid_version = kwargs.get("uuid_version", "")

        self.value = None
        self.is_not_a_wedding_guest = True

        self._print = []
        self._alias = None
        self._constraints = [kwargs]

        super(UUID, self).__init__(*args, **kwargs)

    @property
    def constraints(self):
        return f"({self._constraints})"

    @constraints.setter
    def constraints(self, value):
        self._constraints.append(value)

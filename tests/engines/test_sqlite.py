from asyncio import run, get_event_loop
from unittest import TestCase

from supersql.engines.sqlite import Connection, Engine


class TestConnection(TestCase):
    def setUp(self) -> None:
        pass

    def test_connect_unimplemented(self):
        pass

from unittest import TestCase

from supersql.core.table import Localcache, Table
from supersql.datatypes.base import Base


class Play(Table):
    name = Base()
    age = Base()

class Playful(Table):
    __tablename__ = "playing"


class T(TestCase):
    def test_localcache_instantiation(self):
        localcache = Localcache()
    
    def test_table_instantiation(self):
        table = Table()
    
    def test_tablename(self):
        play = Play()
        play2 = Playful()
        self.assertEqual("play", play.__tablename__)
        self.assertEqual("playing", play2.__tablename__)
    
    def test_get_columns(self):
        _ = ["name", "age"]
        play = Play()
        self.assertEqual(_, play.columns())
    
    def test_get_columns_after_aliasing(self):
        _ = ["playing.name", "playing.age"]
        play = Play()
        play.AS("playing")
        self.assertEqual(_, play.columns())

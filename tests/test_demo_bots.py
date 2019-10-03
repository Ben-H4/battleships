import unittest, math

from world import World
from utilities import *
from constants import *

from bots.random import BattleshipBot as RandoBot
from bots.sequential import BattleshipBot as OCDBot

class TestDemoBots(unittest.TestCase):
    def test_randobot(self):
        world=World(BOARD.WIDTH,BOARD.HEIGHT)
        bot=RandoBot()
        ships=bot.get_setup()
        self.assertTrue(world.is_ships_valid(ships))
        
        hits=world.get_hits()
        shots=world.get_shots()
        
        x,y=bot.get_move(hits,shots)
        self.assertTrue(world.is_in_bounds(x,y))        
        
        points=[bot.get_move(world.get_hits(),world.get_shots()) for i in range(10)]
        self.assertGreater(len(set(points)),1,msg=("\npoints = %s"%str(points)))
    
    def test_ocd_bot(self):
        world=World(BOARD.WIDTH,BOARD.HEIGHT)
        bot=OCDBot()
        ships=bot.get_setup()
        self.assertTrue(world.is_ships_valid(ships))
        
        ship=(2,0,2,False)
        world.set_ship(ship)
        
        for i in range(30):
            result=bot.get_move(world.get_hits(),world.get_shots())
            expected=(i%10,math.floor(i/10))
            self.assertEqual(result,expected,msg=("\n\ni = '%s'"%i))
            world.shoot(*result)
    
import unittest

from utilities import *
from constants import *

class TestUtilities(unittest.TestCase):
    
    def test_script_safe(self):
        path="tests/bot_unsafe1.py"
        self.assertFalse(is_script_safe(path))
        
        path="tests/bot_unsafe2.py"
        self.assertFalse(is_script_safe(path))
        
        path="tests/bot_valid.py"
        self.assertTrue(is_script_safe(path))
        
    def test_get_bot(self):
        path="tests/bot_valid.py"        
        bot = get_bot_from_path(path)
        self.assertTrue(bot)        
        self.assertTrue(is_valid_script(path))
        
    def test_basic_are_ships_valid(self):
        ships=((4,2,2,False),
            (3,2,3,False))
        self.assertTrue(are_ships_valid(ships))
        
    def test_are_ships_valid_overlap(self):
        ships=((4,2,2,False),
            (3,4,2,False))
        self.assertFalse(are_ships_valid(ships))
        
    def test_basic_are_ships_negative_coord(self):
        ships=((4,-1,2,False),
            (3,4,2,False))
        self.assertFalse(are_ships_valid(ships))
        
    def test_basic_are_ships_valid_big_coord(self):
        ships=((4,8,2,False),
            (3,4,2,False))
        self.assertFalse(are_ships_valid(ships))
        
    def test_basic_are_ships_valid_wacky_ship_data(self):
        ships=((4,8,2,False),
            (3,4,2,False),
            (5,5))
        self.assertFalse(are_ships_valid(ships))
        
    def test_basic_are_ships_valid_rotation_overlap(self):
        ships=((4,4,4,False),
            (3,6,3,True))
        self.assertFalse(are_ships_valid(ships))
        
    def test_basic_are_ships_valid_ocd_good_placement(self):
        ships = [(5,2,2,False),
			(4,2,3,False),
			(3,2,4,False),
			(3,2,5,False),
			(2,7,6,True)]
        self.assertTrue(are_ships_valid(ships))
        
    def test_get_ship_coordinates(self):
        ship=(3,2,2,False)
        result=get_ship_coordinates(ship)
        expected=[[2,2],[3,2],[4,2]]
        self.assertEqual(result,expected)
        
        ship=(4,1,1,True)
        result=get_ship_coordinates(ship)
        expected=[[1,1],[1,2],[1,3],[1,4]]
        self.assertEqual(result,expected)
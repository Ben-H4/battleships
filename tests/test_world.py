import unittest

from world import World
from utilities import *
from constants import *

class TestUtilities(unittest.TestCase):
    def test_navy_alive(self):
        world=World(4,4)
        self.assertFalse(world.is_navy_alive())
        
        ship=(2,0,0,False)
        world.set_ship(ship)
        self.assertTrue(world.is_navy_alive())
        
        world.shoot(0,0)
        self.assertTrue(world.is_navy_alive())
        world.shoot(1,0)
        self.assertFalse(world.is_navy_alive())
        
    def test_ships(self):
        world=World(4,4)
        ship=(2,0,0,False)
        self.assertNotIn("T",world.to_string())
        result=world.set_ship(ship)
        self.assertTrue(result)
        self.assertIn("T",world.to_string())
        
    def test_is_ship_valid(self):
        world=World(5,5)
        
        self.assertFalse(is_ship_valid(None))
        
        ship=(3,3,2,False)        
        self.assertTrue(is_ship_valid(ship))
        
        ship=(4,2,2,True)        
        self.assertTrue(is_ship_valid(ship))
        
        ship=(3,2,2)        
        self.assertFalse(is_ship_valid(ship))
        
        ship=(3,-1,2,True)        
        self.assertFalse(is_ship_valid(ship))
        
    def test_valid_ships(self):
        world=World(5,5)
        ships=((5,0,0,False),
            (4,1,1,False),
            (3,0,2,False),
            (3,2,3,False),
            (2,1,4,False))
        for ship in ships:
            self.assertTrue(is_ship_valid(ship))
        
        self.assertTrue(world.is_ships_valid(ships))
        
    def test_invalid_ship_type(self):
        world=World(5,5)
        ships=((5,0,0,7,4),
            (1,1,False),
            (3,"bob",2,False),
            None,
            "not a ship",
            {1:5})
        for ship in ships:
            self.assertFalse(is_ship_valid(ship))
        
    def test_invalid_ships_count(self):
        world=World(5,5)
        ships=((5,0,0,False),
            (4,1,1,False),
            (3,0,2,False),
            (3,2,3,False),
            (2,1,4,False))
        
        self.assertTrue(world.is_ships_valid(ships))
        
        bad_ships=list(ships)
        bad_ships.pop(2)
        self.assertFalse(world.is_ships_valid(bad_ships),msg=str(bad_ships))
        
        bad_ships=list(ships)
        bad_ships.append((5,0,0,False))
        self.assertFalse(world.is_ships_valid(bad_ships))
        
        bad_ships=tuple()
        self.assertFalse(world.is_ships_valid(bad_ships))
        
    def test_invalid_ships_outside(self):
        world=World(10,10)
        ships=((5,0,0,False),
            (4,9,0,True),
            (3,7,9,False),
            (3,5,5,False),
            (2,0,8,True))
        
        self.assertFalse(world._get_invalid_ships_message(ships))
        
        outside_ships=((5,6,0,False),
            (3,29,0,False),
            (3,-1,0,True),
            (4,0,7,True),
            (2,-5,-5,False))
        
        self.assertTrue(world._get_invalid_ships_message(outside_ships))
        for ship in outside_ships:
            self.assertFalse(world.is_ship_in_bounds(ship),msg=str(ship))
            
    def test_ship_sunk_012(self):
        world=World(10,10)
        
        ships=((5,0,0,False),
            (4,9,0,True),
            (3,7,9,False),
            (3,5,5,False),
            (2,0,8,True))
        world.set_ships(ships)
        
        "hits starts as 0 0 0"
        hits=world.get_hits()
        for i in range(3):
            self.assertEqual(hits[5+i][5],0)
        
        "first hit is 1"
        world.shoot(5,5)
        self.assertEqual(world.get_hits()[5][5],1)
        
        "second hit is 1"
        world.shoot(6,5)
        self.assertEqual(world.get_hits()[6][5],1)

        "last hit is 2"
        world.shoot(7,5)
        self.assertEqual(world.get_hits()[7][5],2,msg=str(world.sunk_shots))
        
    def test_ship_sunk_matthew1(self):
        world=World(10,10)
        
        ships = [(5,2,2,False),
                (4,2,3,False),
                (3,2,4,False),
                (3,2,5,False),
                (2,7,6,True)]
        world.set_ships(ships)
        
        "shoot just the troublesome spot and check that it isn't sunk, and equals 1 not 2 or 0."
        world.shoot(4,3)
        self.assertFalse(world.is_ship_sunk(4,3))
        hits=world.get_hits()
        self.assertEqual(hits[4][3],1)
    
    def test_ship_sunk_matthew2(self):
        world=World(10,10)
        
        ships = [(5,2,2,False),
                (4,2,3,False),
                (3,2,4,False),
                (3,2,5,False),
                (2,7,6,True)]
        world.set_ships(ships)
        
        matthew_shots=((9,5),
            (4,7),
            (3,9),
            (9,3),
            (8,8),
            (2,8),
            (4,3))
        for x,y in matthew_shots:
            world.shoot(x,y)
        
        hits=world.get_hits()
        self.assertFalse(world.is_ship_sunk(4,3))
        self.assertEqual(hits[4][3],1)
        
    def test_ship_sunk(self):
        world=World(10,10)
        
        ships=((5,0,0,False),
            (4,9,0,True),
            (3,7,9,False),
            (3,5,5,False),
            (2,0,8,True))
        world.set_ships(ships)
        
        "ocean is not a sunk ship"
        self.assertFalse(world.is_ship_sunk(1,1))
        
        world.shoot(5,5)
        "one hit ship is not sunk, checking the hit position"
        self.assertFalse(world.is_ship_sunk(5,5))
        "one hit ship is not sunk, checking a healthy position on that ship"
        self.assertFalse(world.is_ship_sunk(6,5))
        
        world.shoot(6,5)
        "two hit ship still not sunk"
        self.assertFalse(world.is_ship_sunk(5,5))
        self.assertFalse(world.is_ship_sunk(7,5))
        
        world.shoot(7,5)
        "ship is now sunk on all points"
        self.assertTrue(world.is_ship_sunk(5,5))
        self.assertTrue(world.is_ship_sunk(6,5))
        self.assertTrue(world.is_ship_sunk(7,5))
        
        "ocean is still not a sunk ship"
        self.assertFalse(world.is_ship_sunk(1,1))
      
    def test_invalid_ship_lengths(self):
        world=World(10,10)
        
        "good ship lengths"
        ships=((5,0,0,False),
            (4,9,0,True),
            (3,7,9,False),
            (3,5,5,False),
            (2,0,8,True))
        
        self.assertTrue(lengths_match_ships(BOARD.SHIP_LENGTHS,ships))
        
        "two 5s"
        ships=((5,0,0,False),
            (5,9,0,True),
            (3,7,9,False),
            (3,5,5,False),
            (2,0,8,True))
        self.assertFalse(lengths_match_ships(BOARD.SHIP_LENGTHS,ships))
        
        "length 7"
        ships=((5,0,0,False),
            (4,9,0,True),
            (3,7,9,False),
            (3,5,5,False),
            (7,0,8,True))
        self.assertFalse(lengths_match_ships(BOARD.SHIP_LENGTHS,ships))
        
        "length 1"
        ships=((5,0,0,False),
            (4,9,0,True),
            (3,7,9,False),
            (3,5,5,False),
            (1,0,8,True))
        
        self.assertFalse(lengths_match_ships(BOARD.SHIP_LENGTHS,ships))
        
        "negative length"
        ships=((5,0,0,False),
            (4,9,0,True),
            (3,7,9,False),
            (3,5,5,False),
            (-5,0,8,True))
        
        self.assertFalse(lengths_match_ships(BOARD.SHIP_LENGTHS,ships))
        
    def test_ships_overlap(self):        
        "no overlaps, no rotations"
        ships=((5,0,0,False),
            (4,1,1,False),
            (3,0,2,False),
            (3,2,3,False),
            (2,1,4,False))
        
        self.assertFalse(do_ships_overlap(ships))
        
        "no overlaps, with rotations"
        ships=((5,0,0,False),
            (4,9,0,True),
            (3,7,9,False),
            (3,6,8,False),
            (2,8,2,True))
        
        self.assertFalse(do_ships_overlap(ships))
        
        "no rotation overlap"
        ships=((4,2,0,False),
            (4,5,0,False))
        
        self.assertTrue(do_ships_overlap(ships))
        
        "with rotation overlap"
        ships=((4,2,1,False),
            (4,4,0,True))
        
        self.assertTrue(do_ships_overlap(ships))
        
        
        
        
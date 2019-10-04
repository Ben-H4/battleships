import random

from constants import *

# Duplicate the template you plan to use and rename it your fleet name

class BattleshipBot():
    def __init__(self):
        self.ship_name = "SS Random"  # Name of Fleet
        self.commander_name = "Random"  # Name of Commander

    def get_setup(self):
        ships = [
            # (ship-size, x-cord, y-cord, vertical-orientation)
            # Do not change the ship-size
            # x-cord and y-cord are between 0-9
            (5, 2, 2, False),
            (4, 2, 4, False),
            (3, 2, 6, False),
            (3, 2, 8, False),
            (2, 7, 6, False)
        ]
        return ships

    def get_move(self, hits, shots):
        "returns a random move."
        return random.randint(0,BOARD.WIDTH-1),random.randint(0,BOARD.HEIGHT-1)
    
    def get_iteration_move(self, hits, shots):
        "iterates over shots systematically until it finds some move."
        for i in range(len(shots)):
            for j in range(len(shots[0])):
                if not shots[i][j]:
                    return i,j
        return 0,0

    # Test your bot:
    # python3.6 battleship.py match bots/<your bot name>.py bots/<random/sequential>.py --verbose --wait=0.1



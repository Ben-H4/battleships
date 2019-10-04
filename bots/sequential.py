from constants import *

# Duplicate the template you plan to use and rename it your fleet name

class BattleshipBot():
    def __init__(self):
        self.ship_name = "SS Sequential"  # Name of Fleet
        self.commander_name = "Sequential"  # Name of Commander

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

        for j in range(BOARD.WIDTH):
            for i in range(BOARD.HEIGHT):
                if not shots[i][j]:
                    return i, j
        return 0, 0

    # Test your bot:
    # python3.6 battleship.py match bots/<your bot name>.py bots/<random/sequential>.py --verbose --wait=0.1

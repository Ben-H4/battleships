class BOARD:
    WIDTH = 10
    HEIGHT = 10
    SHIP_LENGTHS = (5, 4, 3, 3, 2)


BOARD.SHIP_COUNT = len(BOARD.SHIP_LENGTHS)

BENCHMARK_BOT_PATH="bots/commodore_bench.py"

class OUTCOMES:
    PLAYER1_WIN = 0
    PLAYER2_WIN = 1
    IN_PROGRESS = 2
    DRAW = 3


class SHIPS_ERROR:
    BASIC_TYPE="ships is a bad type"
    COUNT="wrong number of ships"
    INVALID="invalid ship"
    LENGTH="weird ship length"
    SHIP_COUNT="wrong number of ships"
    DUPLICATE_LENGTH="too many ships with this length"
    OUTSIDE="a ship is outside the world limits"
    OVERLAPPING="ships overlap"
    TOUCHING="ships are touching"
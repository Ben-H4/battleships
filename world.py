import copy

from constants import *
from utilities import *


class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ship_counter = 0

        self.shots = [[0 for i in range(height)] for j in range(width)]
        self.ships = [[0 for i in range(height)] for j in range(width)]
        
        "A set of all shots, if any, that was the last shot on a ship that sunk it."
        self.sunk_shots = set()

    def get_tuple_array(self, array):
        "Takes a 2D array and converts it, and its inner items to tuples instead of lists."
        return tuple([tuple([a for a in column]) for column in array])

    def get_shots(self):
        "Returns a tuple array where 0 has never been shot at, 1 has."
        return self.get_tuple_array(self.shots)

    def get_ships(self):
        return self.get_tuple_array(self.ships)

    def get_hits(self):
        """Returns a 2D array.
        0 means no was hit in this cell.
        1 means a ship has been hit here.
        2 means a ship has been hit here, and it sunk the ship."""
        hits = copy.deepcopy(self.ships)
        for i in range(self.width):
            for j in range(self.height):
                if self.ships[i][j]:
                    hits[i][j]=1 if self.shots[i][j] else 0
        for sunk_shot in self.sunk_shots:
            hits[sunk_shot[0]][sunk_shot[1]]=2
        return hits

    def shoot(self, x, y):
        "Shoots this cell."
        new_shot=not self.shots[x][y]
        self.shots[x][y] = 1
        if new_shot and self.is_ship_sunk(x,y):
            self.sunk_shots.add((x,y))        
        
    def is_ship_sunk(self,x,y):
        "Returns true if there is a ship at this position and it is completely sunk."
        ship_id=self.ships[x][y]
        if not ship_id:
            return False
        
        for i in range(self.width):
            for j in range(self.height):
                if self.ships[i][j]==ship_id and not self.shots[i][j]:
                    return False
        return True        

    def is_navy_alive(self):
        "Returns true if at least one ship cell is not hit yet."
        for i in range(self.width):
            for j in range(self.height):
                if self.ships[i][j] and not self.shots[i][j]:
                    return True
        return False

    def set_ships(self, ships):
        "Returns true if no errors were encountered."
        for ship in ships:
            if not self.set_ship(ship):
                return False
            
        if len(ships) != BOARD.SHIP_COUNT:
            return False
        
        lengths=[ship[0] for ship in ships]
        unused_lengths=list(copy.copy(BOARD.SHIP_LENGTHS))
        for i in lengths:
            if i not in unused_lengths:
                return False
            unused_lengths.remove(i)
        
        return True

    def set_ship(self, ship):
        """Returns True if no errors were encountered."""
        if not is_ship_valid(ship):
            return False

        self.ship_counter += 1
        ship_id = self.ship_counter
        for x, y in get_ship_coordinates(ship):
            if self.ships[x][y]:
                return False
            self.ships[x][y] = ship_id
        return True

    def is_in_bounds(self, x, y):
        return x >= 0 and y >= 0 and x < self.width and y < self.height

    def is_ship_in_bounds(self, ship):
        ship_length, x, y, rotation = ship
        coordinates=get_ship_coordinates(ship)
        if not coordinates:
            return False
        for x, y in coordinates:
            if not self.is_in_bounds(x, y):
                return False
        return True
    
    def is_ships_valid(self,ships):
        return not self._get_invalid_ships_message(ships)

    def _get_invalid_ships_message(self, ships):
        "If ships is invalid, returns a message describing how. Returns an empty string if ships is valid."

        if not ships or type(ships) not in (tuple, list):
            return SHIPS_ERROR.BASIC_TYPE
        
        if len(ships) != BOARD.SHIP_COUNT:
            return SHIPS_ERROR.COUNT

        for ship in ships:
            if not self.is_ship_in_bounds(ship):
                return SHIPS_ERROR.OUTSIDE+" "+str(ship)
            if not is_ship_valid(ship):
                return SHIPS_ERROR.INVALID+" "+str(ship)

        if (lengths_match_ships(BOARD.SHIP_LENGTHS,ships)):
            return get_ship_lengths_message(BOARD.SHIP_LENGTHS,ships)
        
        if do_ships_overlap(ships):
            return get_overlap_ships_message(ships)
        
        return ""

    def show(self, label, other_world=None):
        print(label)
        print(self.to_string(other_world=other_world))

    def to_string(self, other_world=None):
        "Returns a string that can be printed to display the state of the world."
        hits = self.get_hits()
        spacing = "        "
        lines = []
        for j in range(self.height):
            lines.append(spacing)
            for i in range(self.width):
                if hits[i][j]:
                    lines[-1] += " X"
                elif self.shots[i][j]:
                    lines[-1] += " O"
                elif self.ships[i][j]:
                    lines[-1] += " T"
                else:
                    lines[-1] += " ~"

        if other_world:
            other_lines = other_world.to_string().split("\n")
            for i in range(len(lines)):
                lines[i] = lines[i] + spacing + other_lines[i]
        return "\n".join(lines)

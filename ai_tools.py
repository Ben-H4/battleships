from constants import *
from utilities import *

"""This module contains generic, useful functions for battleship AI."""

def get_next_diagonal_shot(shots):
    """There are ten diagonal shots: (0,0), (1,1), (2,2) ... etc.
    This returns the next diagonal point that has not yet been shot.
    Or it returns None if all diagonal points have been shot."""
    for i in range(BOARD.WIDTH):
        if not shots[i][i]:
            return i,i
    return None

def get_next_diagonal_shot_reversed(shots):
    """This is just like get_next_diagonal_shot, except instead of bottom left to top right,
    the diagonal is top left to bottom right."""
    for i in range(BOARD.WIDTH):
        y=BOARD.WIDTH-i-1
        if not shots[i][y]:
            return i,y
    return None

def has_shot_all_corners(shots):
    """Returns true if all corners have been shot."""
    return not bool(get_next_unshot_corner(shots))

def get_next_unshot_corner(shots):
    """Returns a corner point that has not yet been shot.
    If all corners have been shot, returns None."""
    for x,y in ((0,0),(BOARD.WIDTH-1,0),(0,BOARD.HEIGHT-1),(BOARD.WIDTH-1,BOARD.HEIGHT-1)):
        if not shots[x][y]:
            return x,y
    return None


def get_next_unshot_point(shots):
    """Just like OCD bot, this returns the next point that has not been shot.
    If all points have been shot, returns None."""
    for i in range(BOARD.WIDTH):
        for j in range(BOARD.HEIGHT):
            if not shots[i][j]:
                return i,j
    return None

def get_next_unshot_checkerboard_point(shots):
    """This returns the next unshot point, but only if it's a black square on a chess board.
    If all black chess board squares have been shot, returns None."""
    for i in range(BOARD.WIDTH):
        for j in range(BOARD.HEIGHT):
            if (i+j)%2:
                continue
            if not shots[i][j]:
                return i,j
    return None

def is_inside_board(x,y):
    """Given a position (x,y), returns True if (x,y) is
    a position inside the board, like (0,0) or (5,3).
    returns False if (x,y) is outside of the board, like (-1,5) or (10,5)."""
    return x>=0 and x<BOARD.WIDTH and y>=0 and y<BOARD.HEIGHT

def has_unshot_adjacent_points(x,y,shots):
    """Returns true if the point (x,y) has at least one point up, down, left, or right from it that is not shot."""
    return get_explore_spot(x,y,shots,shots)

def get_explore_spot(x,y,shots):
    """Returns a point adjacent to (x,y) that is not shot.
    Or, if all four points surrounding (x,y) are shot, returns None. For example:
    
    . . o .
    . o x .
    . . o .
    . . . .
    
    Where:
      "." means water that has not been shot.
      "o" means water that has been shot.
      "x" means a ship that has been shot.
      
    "x" is at position (2,2). So:
      get_explore_shot(2,2,hits,shots)
    will return:
      (3,2)
    because the point to the right is unshot, and may have a ship in it."""
    
    for xoffset,yoffset in ((-1,0),(1,0),(0,-1),(0,1)):
        x2=x+xoffset
        y2=y+yoffset
        if is_inside_board(x2,y2) and not shots[x2][y2]:
            return x2, y2
    return None
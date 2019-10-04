import importlib.util
import os
import os.path
import re
import sys
import traceback
import copy
import string

from constants import *

def get_next_log_path(label="game"):
    folder = "logs"
    if not os.path.isdir(folder):
        os.makedirs(folder)

    def get_path(i):
        return "logs" + os.sep + label+"-%s.log" % str(i).zfill(5)

    i = 1
    while os.path.isfile(get_path(i)):
        i += 1
    return get_path(i)


def get_matching_paths_recursively(rootdir, extension, verbose=0):
    "Returns a list of full paths. Searches 'rootdir' recursively for all files with 'extension'."
    if verbose:
        print("Getting filenames for files with extension \"%s\" at:\n%s" %
              (extension, rootdir))
    results = []
    for root, _, filenames in os.walk(rootdir):
        for filename in filenames:
            if filename.find(extension) == len(filename) - len(extension):
                path = os.path.join(root, filename)
                results.append(path)
    return results

def lengths_match_ships(lengths,ships):
    return not bool(get_ship_lengths_message(lengths,ships))

def is_ship_in_world(ship):
    """Returns true if every position occupied by this ship is inside the world.
    Also returns false if ship is invalid."""
    if not is_ship_valid(ship):
        return False
    for x,y in get_ship_coordinates(ship):
        "Corner One"
        if (x<2 and y<1) or (x<1 and y<2):
          return False
        "Corner Two"    
        if (x>7 and y<1) or (x>8 and y<2):
          return False
        "Corner Three"
        if (y>7 and x>8) or (y>8 and x>7):
          return False
        "Corner Four"
        if (y>7 and x<1) or (x<2 and y>8):
            return False
        "Finally check the actual boundaries of the board"    
        if x>=BOARD.WIDTH or y>=BOARD.HEIGHT:
            return False
    return True
    

def are_ships_valid(ships):
    "Returns true if every ship is valid, can be placed in the world, and they do not overlap."
    "Note: does not check if lengths are correct."
    for ship in ships:
        if not is_ship_valid(ship):
            return False
        if not is_ship_in_world(ship):
            return False        
    return not do_ships_overlap(ships)


def is_ship_valid(ship):
    "Returns True if this ship is valid ship data, and can be placed in some world."
    if not ship or type(ship) not in (tuple, list) or len(ship) != 4:
        return False
    for c in ship[:3]:
        if type(c) is not int or c<0:
            return False
    if ship[3] not in (True,False,0,1):
        return False
    ship_length,x,y,rotation=ship
    if x<0 or y<0:
        return False
    return True

def get_ship_lengths_message(lengths,ships):
    "Returns an empty string if ships lengths are correct. If they aren't returned string describes the failure."
    
    if len(lengths) != len(ships):
        return SHIPS_ERROR.SHIP_COUNT
    
    unused_lengths = list(copy.copy(lengths))
    for ship in ships:
        ship_length = ship[0]
        if ship_length not in lengths:
            return SHIPS_ERROR.LENGTH + str(ship) + " length = '%s'" % str(ship_length)
        if ship_length not in unused_lengths:
            return SHIPS_ERROR.DUPLICATE_LENGTH + str(ship) + " length = '%s'" % str(ship_length)
        unused_lengths.remove(ship_length)
    return ""

def do_ships_overlap(ships):
    return bool(get_overlap_ships_message(ships))

def get_overlap_ships_message(ships):
    "Returns an empty string if ships do not overlap. If they do, returned string describes the overlap."
    used_coords=set()
    for ship in ships:
        for xy in get_ship_coordinates(ship):
            coord=tuple(xy)
            if coord in used_coords:
                return "overlapping ships detected. (x,y)="+str(xy)+" ship="+str(ship)
            used_coords.add(coord)
    return ""

def do_ships_touch(ships):
    return bool(get_touching_ships_message(ships))
    
def get_touching_ships_message(ships):
    "Returns an empty string if ships do not touch. If they do, returned string describes the overlap."
    used_coords=set()
    count = 0
    for ship in ships:
        count += 1
        ship_id = count
        for x, y in get_ship_coordinates(ship):
            coord = (x,y,ship_id)
            if any([True for t in used_coords if t[0]==x+1 and t[1]==y and t[2]!=ship_id]):
                return "touching ships detected. (x,y)="+str((x,y))+" ship="+str(ship)
            if any([True for t in used_coords if t[0]==x-1 and t[1]==y and t[2]!=ship_id]):
                return "touching ships detected. (x,y)="+str((x,y))+" ship="+str(ship)
            if any([True for t in used_coords if t[0]==x and t[1]==y+1 and t[2]!=ship_id]):
                return "touching ships detected. (x,y)="+str((x,y))+" ship="+str(ship)
            if any([True for t in used_coords if t[0]==x and t[1]==y-1 and t[2]!=ship_id]):
                return "touching ships detected. (x,y)="+str((x,y))+" ship="+str(ship)
                
            used_coords.add(coord)
    return ""
    
def get_ship_coordinates(ship):
    """Given ship parameters, returns a list of coordinates this ship will occupy. Example:
    
    get_ship_coordinates(3,0,4,True)    returns    ((0,4),(0,5),(0,6))
    """
    
    if not is_ship_valid(ship):
        return []
    
    ship_length, x, y, rotation = ship
    x_vector = 0 if rotation else 1
    y_vector = 1 if rotation else 0
    return [[x + x_vector * i, y + y_vector * i] for i in range(ship_length)]


def get_versus_log_path(bot1,bot2):
    def safe_name(text):
        if not text or len(text)==0:
            return "unknown"
        safe=string.ascii_letters+string.digits
        text=text.lower()[:20]
        return "".join([c for c in text if c in safe])
    
    name1=safe_name(bot1.ship_name)
    name2=safe_name(bot2.ship_name)
        
    label=name1+"-versus-"+name2
    return get_next_log_path(label=label)

def get_bot_from_path(path, verbose=False):
    spec = importlib.util.spec_from_file_location("bot", path)
    if not spec:
        return None
    module = spec.loader.load_module()
    spec.loader.exec_module(module)
    return module.BattleshipBot()

def get_bot_paths(folder,verbose=True):
    paths=[]
    for filename in os.listdir(folder):
        if not filename.endswith(".py"):
            continue
        path=folder+os.sep+filename
        if is_valid_script(path,verbose=verbose):
            paths.append(path)
        else:
            print("")
    return paths

def is_valid_script(path, verbose=False):
    "Is this bot script path valid and probably safe?"
    if not os.path.isfile(path) or not path or not path.endswith(".py"):
        if verbose:
            print("Invalid script. Not a python script file: '%s'" % path)
        return False

    if not is_script_safe(path, verbose=verbose):
        if verbose:
            print("Invalid script. Unsafe script: '%s'" % path)
        return False

    try:
        bot = get_bot_from_path(path, verbose=verbose)
    except:
        if verbose:
            print("Script failed to import: '%s'"%path)
            traceback.print_exc(limit=2, file=sys.stdout)
        return False

    required_attributes = ("ship_name", "commander_name", "get_move", "get_setup")
    for a in required_attributes:
        if a not in dir(bot):
            if verbose:
                print("Invalid script. Missing attribute or function: '%s'" % a)
            return False
    return True

def is_import_line_safe(line):
    if line.startswith("#"):
        return True
    if "import " not in line:
        return True
    
    for white in ("random","constants","utilities","copy","ai_tools"):
        for a in ("from %s import ","import %s"):
            if a%white in line:
                return True
    return False


def is_script_safe(path, verbose=False):
    "Performs basic but holy security checks on the script, verify that it probably can't do too many evil things."
    with open(path, "r") as f:
        data = f.read()
    lines = data.split("\n")

    bad_regexes = ("exec[ ]*\\(", "open[ ]*\\(")
    for line in lines:
        if not is_import_line_safe(line):
            if verbose:
                print("Unsafe Python script. Bad import: '%s'"%line)
            return False
        for r in bad_regexes:
            if re.findall(r, line):
                if verbose:
                    print("Unsafe Python script. Found code matching pattern: '%s'" % r)
                return False
    return True

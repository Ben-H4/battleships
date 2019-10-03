"""
Battleship Game Manager

Usage:
  battleship.py match <player1-script-path> <player2-script-path> [options]
  battleship.py test
  battleship.py robin <bots-folder> [options]
  battleship.py benchmark <bots-folder> [options]
  battleship.py heatmap <log-folder>

Options:
  --rounds=<count>            Play this many rounds for 'match', 'robin', or 'benchmark' mode. [default: 1]
  --max-turns=<count>         Games that last this long are declared a draw. [default: 250]
  --verbose
  --wait=<seconds>            Wait this many seconds between turns. Useful for viewing. [default: 0]
  --logging                   Write log files for every game to the 'logs' folder.
  
  -h --help           Show this screen.
  -v --version        Show version.
"""

import os.path
import unittest
import sys, json
from itertools import combinations
from collections import Counter

from docopt import docopt
from game import Game
from utilities import *


def run_unit_tests():
    paths = get_matching_paths_recursively("tests", ".py")
    modules = [path[:-3].replace(os.sep, ".") for path in paths]
    suites = [unittest.defaultTestLoader.loadTestsFromName(m) for m in modules]
    test_suite = unittest.TestSuite(suites)
    text_runner = unittest.TextTestRunner().run(test_suite)

def run_match(bot1path,bot2path,rounds,wait_seconds,max_turns,logging,verbose):
    bot1 = get_bot_from_path(bot1path, verbose=verbose)
    bot2 = get_bot_from_path(bot2path, verbose=verbose)
    if bot1 and bot2:
        bot1_wins_this_match=0
        bot2_wins_this_match=0
        draws=0
        for round_number in range(rounds):
            game = Game(bot1, bot2, verbose=verbose, wait_seconds=wait_seconds, max_turns=max_turns)
            if logging:
                game.write_log()
                
            if game.outcome == OUTCOMES.PLAYER1_WIN:
                bot1_wins_this_match+=1
            elif game.outcome == OUTCOMES.PLAYER2_WIN:
                bot2_wins_this_match+=1
            else:
                draws+=1
            
        print("\nBattleship computed %s game%s."%(rounds,"" if rounds==1 else "s"))
        print(game.get_ship_name(bot1)+" won %s/%s rounds."%(bot1_wins_this_match,rounds))
        print(game.get_ship_name(bot2)+" won %s/%s rounds."%(bot2_wins_this_match,rounds))
        if draws:
            print("%s draws."%draws)
            
    else:
        print("Cannot setup match. At least one bot failed to load.\nbot1 = '%s'\nbot2 = '%s'" % (bot1, bot2))

def run_robin(bots_folder,max_turns,logging,verbose,rounds=1):
    "Runs a round robin tournment for all the bots in the given bots folder."
    paths=get_bot_paths(bots_folder,verbose=verbose)
    bots=[get_bot_from_path(path) for path in paths if is_valid_script(path,verbose=True)]
    print("Starting round robin tournament for %s bots."%len(bots))
    
    history={bot:[0,0,0] for bot in bots} #(wins,losses,draws)
    win_total={bot:0 for bot in bots}
    
    for bot1, bot2 in combinations(bots,2):
        bot1_wins_this_match=0
        bot2_wins_this_match=0
        for i in range(rounds):
            game = Game(bot1, bot2, verbose=False, wait_seconds=0, max_turns=max_turns)
            if logging:
                path=get_versus_log_path(bot1,bot2)
                game.write_log(path=path)
                path=get_versus_log_path(bot2,bot1)
                game.write_log(path=path)
            
            if game.outcome == OUTCOMES.PLAYER1_WIN:
                bot1_wins_this_match+=1
                win_total[bot1]+=1
            elif game.outcome == OUTCOMES.PLAYER2_WIN:
                bot2_wins_this_match+=1
                win_total[bot2]+=1
                
        if bot1_wins_this_match>bot2_wins_this_match:
            history[bot1][0]+=1
            history[bot2][1]+=1
        elif bot1_wins_this_match<bot2_wins_this_match:
            history[bot1][1]+=1
            history[bot2][0]+=1
        else:
            history[bot1][2]+=1
            history[bot2][2]+=1
    
    scored_bots=[(history[bot][0]*3+history[bot][2],bot) for bot in bots]
    sorted_bots=reversed(sorted(scored_bots,key=lambda x:x[0]))
    print("")
    rank_strings={0:"FIRST PLACE",1:"SECOND PLACE",2:"THIRD PLACE"}
    games_per_bot=(len(bots)-1)*rounds
    for rank,item in enumerate(sorted_bots):
        score,bot=item
        wins=win_total[bot]
        win_percent=round(100*wins/games_per_bot,2)
        print(rank_strings.get(rank,str(rank+1))+": '%s' by %s"%(bot.ship_name,bot.commander_name))
        print("         %s Points. %s Wins. %s Losses. %s Draws."%(score,history[bot][0],history[bot][1],history[bot][2]))
        if rounds>1:
            print("         %s total wins. Won %s%% of %s games."%(wins,win_percent,games_per_bot))
        print("")

def run_heatmap(log_folder,verbose):
    "Parse log files to find ship placement and shot statistics."
    "This function is hacky, untested, and very sensitive to log format changes."
    if not os.path.isdir(log_folder):
        print("Cannot generate heatmap. Not a folder: '%s'"%log_folder)
        return
    
    paths=get_matching_paths_recursively(log_folder,".log")
    ship_heatmap=[[0 for i in range(BOARD.HEIGHT)] for j in range(BOARD.WIDTH)]
    shot_heatmap=[[0 for i in range(BOARD.HEIGHT)] for j in range(BOARD.WIDTH)]
    
    for path in paths:
        with open(path,"r") as f:
            data=f.read()
        
        setup_count=0
        delimit=" ships = [("
        for line in data.split("\n"):
            if delimit in line:
                setup_count+=1
                ship_string=line.split(delimit[:-2])[1].lower().replace("(","[").replace(")","]")
                ships=json.loads(ship_string)
                for ship in ships:
                    for x,y in get_ship_coordinates(ship):
                        ship_heatmap[x][y]+=1                
                if setup_count>1:
                    break
        
        r="shoots at \\([\\d],[\\d]\\)"
        shots=re.findall(r,data)
        for shot in shots:
            shot_string=shot[10:].replace("(","[").replace(")","]")
            xy=json.loads(shot_string)
            shot_heatmap[xy[0]][xy[1]]+=1
    
    generate_heatmap_html(ship_heatmap,shot_heatmap)

def generate_heatmap_html(ships,shots):
    folder="heatmaps"
    os.makedirs(folder,exist_ok=True)
    
    def get_heatmap_table_html(array,monochrome=False):
        max_value=max([max(row) for row in array])
        html="<table>"
        for j in range(BOARD.HEIGHT):
            html+="\n<tr>"
            for i in range(BOARD.WIDTH):
                ratio=array[i][j]/max_value
                if monochrome:
                    c=round(255*ratio)
                    color="rgb(%s,%s,%s)"%(c,c,c)
                else:
                    r=round(255-255*ratio)
                    g=round(255*ratio)
                    color="rgb(%s,%s,0)"%(r,g)
                html+="""\n<td style="background-color: %s;"> </td>"""%color
            html+="\n</tr>"
        
        html+="</table>"
        return html
    
    html="<style>td { padding: 30px }</style>"
    html+="\n\n<h1>Heatmap for ship placement</h1>"+get_heatmap_table_html(ships)
    html+="\n\n<h1>Heatmap for shots</h1>"+get_heatmap_table_html(shots)
    html+="\n\n<h1>Heatmap for ship placement (monochrome)</h1>"+get_heatmap_table_html(ships,True)
    html+="\n\n<h1>Heatmap for shots (monochrome)</h1>"+get_heatmap_table_html(shots,True)
    
    with open(folder+"/heatmap.html","w") as f:
        f.write(html)

def run_benchmark(bots_folder,max_turns,logging,verbose,rounds=1):
    "Runs a benchmark for all the bots in the given bots folder."
    
    if not os.path.isfile(BENCHMARK_BOT_PATH):
        print("Cannot benchmark. Missing Commodore Bench script: '%s'"%BENCHMARK_BOT_PATH)
        return
    
    paths=get_bot_paths(bots_folder,verbose=verbose)
    bots=[get_bot_from_path(path) for path in paths if is_valid_script(path,verbose=True)]
    print("Starting benchmark for %s bots."%len(bots))
    
    wins={bot:0 for bot in bots}
    bench_bot=get_bot_from_path(BENCHMARK_BOT_PATH)
    
    for bot in bots:
        for i in range(rounds):
            game = Game(bot, bench_bot, verbose=False, wait_seconds=0, max_turns=max_turns)
            if logging:
                path=get_versus_log_path(bot,bench_bot)
                game.write_log(path=path)
                
            if game.outcome == OUTCOMES.PLAYER1_WIN:
                wins[bot]+=1
    
    scored_bots=[(wins[bot],bot) for bot in bots]
    sorted_bots=reversed(sorted(scored_bots,key=lambda x:x[0]))
    print("")
    rank_strings={0:"FIRST PLACE",1:"SECOND PLACE",2:"THIRD PLACE"}
    for rank,item in enumerate(sorted_bots):
        player_wins,bot=item
        win_percent=round(100*player_wins/rounds,2)
        print(rank_strings.get(rank,str(rank+1))+": '%s' by %s"%(bot.ship_name,bot.commander_name))
        print("         %s total wins against Commodore Bench. Won %s%% of %s games."%(player_wins,win_percent,rounds))

def main(args):
    try:
        rounds = int(args["--rounds"])
        if rounds < 1:
            rounds = 1
    except:
        print("ABORT. Invalid round count: %s" % args["--rounds"])
        return

    try:
        wait_seconds = float(args["--wait"])
    except:
        print("ABORT. Invalid wait_seconds: %s" % args["--wait"])
        return
    
    try:
        max_turns = int(args["--max-turns"])
    except:
        print("ABORT. Invalid max_turns: %s" % args["--max_turns"])
        return

    verbose = args["--verbose"]

    if args["match"]:
        run_match(args["<player1-script-path>"],
                  args["<player2-script-path>"],
                  rounds,wait_seconds,max_turns,args["--logging"],verbose)
    elif args["test"]:
        run_unit_tests()
    elif args["robin"]:
        run_robin(args["<bots-folder>"],max_turns,args["--logging"],verbose,rounds=rounds)
    elif args["benchmark"]:
        run_benchmark(args["<bots-folder>"],max_turns,args["--logging"],verbose,rounds=rounds)
    elif args["heatmap"]:
        run_heatmap(args["<log-folder>"],verbose)

def is_windows_and_no_cli_args():
    return os.name=="nt" and len(sys.argv)==1

if __name__ == "__main__":
    if is_windows_and_no_cli_args():
        print("""\nGood job! You were able to run the battleship.py script on your computer. One problem though...
To tell the battleship.py code what to do, you need to write command line instructions.
Since you're on Windows, some extra steps need to be taken to set this up.
You need to Google "set up python in windows command line" and follow those instructions.
Then run the command line or "cmd" program, and type this command:
    python3 battleship.py match bots/sequential.py bots/random.py --verbose --wait=0.1
Instead of using Windows, you could use Linux instead where things are already set up for Python.

If after all of that you're still having trouble, try asking a friend or another student for help.""")
        input("\nPress Enter to Exit\n")
    else:
        args = docopt(__doc__, version="1.0")
        main(args)

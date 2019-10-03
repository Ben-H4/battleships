import random

import time

from constants import *
from utilities import *
from world import World


class Game:
    def __init__(self, bot1, bot2, autostart=True, verbose=False, wait_seconds=0,max_turns=1000):
        self.verbose = verbose
        self.round_counter = 0
        self.winner = -1
        self.wait_seconds = wait_seconds
        self.log_entries = []
        self.max_turns=max_turns

        self.worlds = (World(BOARD.WIDTH, BOARD.HEIGHT), World(BOARD.WIDTH, BOARD.HEIGHT))
        self.bots = (bot1, bot2)
        self.outcome = OUTCOMES.IN_PROGRESS

        if autostart:
            self.play()

    def setup(self):
        for player in range(2):
            world = self.worlds[player]
            bot = self.bots[player]

            try:
                ships = bot.get_setup()
            except:
                self.set_loser(player, message="Ship setup crashed.")
                self.log_exception()
                return False

            self.log("Player %s ships = " % (player + 1) + str(ships))
            if not world.set_ships(ships):
                self.set_loser(player, message="Bad ship setup.")
                return False
        return True

    def log_exception(self):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        text = "\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.log(text)

    def log(self, text):
        self.log_entries.append(text)
        if self.verbose:
            print(text)
            
    def set_draw(self):
        message="Game declared a draw - maximum turns of %s reached."%self.max_turns
        self.log(message)
        self.winner = -1
        self.outcome=OUTCOMES.DRAW

    def set_loser(self, player_index, message=""):
        self.set_winner((player_index + 1) % 2, message=message)

    def set_winner(self, player_index, message=""):
        if message:
            self.log(message)
        self.winner = player_index

        if player_index == 0:
            self.outcome = OUTCOMES.PLAYER1_WIN
        elif player_index == 1:
            self.outcome = OUTCOMES.PLAYER2_WIN
        else:
            raise ValueError("set_winner got a bad player_index = '%s'" % player_index)

    def get_ship_name(self, bot):
        try:
            return bot.ship_name
        except:
            return "Unknown"

    def play(self):
        "This uses bot1 and bot2 to setup the board and play until the game ends."
        if not self.setup():
            return

        player = random.randint(0, 1)
        while self.outcome == OUTCOMES.IN_PROGRESS:
            other_player = player
            player = (player + 1) % 2
            world = self.worlds[player]
            other_world = self.worlds[other_player]
            bot = self.bots[player]
            player_label = "Player %s (%s)" % (player + 1, self.get_ship_name(bot))

            hits = other_world.get_hits()
            shots = other_world.get_shots()

            self.round_counter += 1

            if self.round_counter == 1:
                message = "%s gets the first move." % (player_label)
                self.log(message)
                
            if self.round_counter>self.max_turns:
                self.set_draw()
                break

            "print and log displays for both board worlds"
            label = "Round %s" % self.round_counter
            output = self.worlds[0].to_string(other_world=self.worlds[1])
            self.log(label + "\n" + output)

            "get shoot at coordinates"
            try:
                x, y = bot.get_move(hits=hits, shots=shots)
                assert type(x) is int
                assert type(y) is int
            except:
                self.set_loser(player, message="'%s' crashed during its turn." % self.get_ship_name(bot))
                self.log_exception()
                break

            "shoot those coordinates, print, and log."
            message = "%s shoots at (%s,%s)" % (player_label, x, y)
            self.log(message)
            other_world.shoot(x, y)
            if not other_world.is_navy_alive():
                self.set_winner(player)
                break

            time.sleep(self.wait_seconds)
            
        text="Game over! "
        if self.outcome == OUTCOMES.DRAW:
            text+="Draw."
        else:
            text += "The winner is '%s'" % self.get_winner_label()
        self.log(text)

    def write_log(self,path=None):
        if not path:
            path = get_next_log_path()
        with open(path, "w") as f:
            f.write("\n".join(self.log_entries))

    def get_winner_label(self):
        if self.winner == -1:
            return "Unknown"
        bot = self.bots[self.winner]
        return bot.ship_name

    def show_winner(self):
        a = {OUTCOMES.DRAW: "Draw", OUTCOMES.IN_PROGRESS: "Not Started",
             OUTCOMES.PLAYER1_WIN: "Player 1 Win", OUTCOMES.PLAYER2_WIN: "Player 2 Win"}
        print("Game result: %s" % a.get(self.outcome, "Unknown"))

    def get_log_header(self):
        try:
            player1 = "Player 1: " + self.bots[0].ship_name
        except:
            player1 = "Player 1: (Unknown bot)"

        try:
            player2 = "Player 2: " + self.bots[1].ship_name
        except:
            player2 = "Player 2: (Unknown bot)"

        header = "Battleship game log."
        header += "\n" + datetime.datetime.now()
        header += "\n" + player1
        header += "\n" + player2
        header += "\nWinner: " + self.get_winner_label()
        header += "*" * 40 + "\n\n"
        return header

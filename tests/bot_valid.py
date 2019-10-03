
"This is the absolute minimum bot to pass module loading tests."

class BattleshipBot():
	def __init__(self):
		self.ship_name="test bot"
		self.commander_name="bobjoe"
	
	def get_move(self, hits, shots):
		return 0,0
	
	def get_setup(self):
		return []
	




import re

class match_scenario:

	def __init__(self, str):
		self.str = str
		self.match = None	

		match = re.findall(r'_[a-z]+\d\d\d_', self.str)
		if match:
			self.match = match[0]
		
		self._return_match()
		
	def _return_match(self):
		return self.match

	def format(self):
		if self.match is not None:
			match_char = list(self.match)[1:-1]
			fromatted_str = ''.join(match_char[:3])+match_char[3]+'-'+match_char[4]+'.'+match_char[5]

			return fromatted_str.upper()
		else:
			return


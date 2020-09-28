import sys
import os
sys.path.insert(0, os.path.abspath(os.getcwd()) + '\\venv\\Lib\\site-packages\\pip-19.0.3-py3.7.egg\\pip\\_vendor')

from pyparsing import *

class Parser():

	def __init__(self, param, is_setting):
		self.setting_types = []
		self.results = []

		if is_setting:
			self.parse_conf(param)
		else:
			self.parse_algo(param)

	def parse_conf(self, filename):
		data_file = self.open_file(filename)
		self.parse_append_types(Word(alphas + '_') + Suppress('=') + Word(nums + '.'), 1)
		self.parse_append_types(Word(alphas + '_') + Suppress('=') + Word(nums), 1)
		self.parse_append_types(
			Word(alphanums + '_-.') + Suppress('=') + OneOrMore(Word(alphanums + '_-.')),
			0)  # need to be > 0 if next rules

		j = 0
		for i in range(len(data_file)):
			if len(data_file[i]) <= 1 or data_file[i][0] == '*': continue
			list = self.setting_types[j][0].parseString(data_file[i]).asList()
			if len(list) == 0:
				print("Error while parsing the file. Check it again")
				break
			self.results.append(list)
			self.setting_types[j][1] -= 1
			if self.setting_types[j][1] == 0: j += 1

	def parse_algo(self, data):
		data_file = data.split('\n')
		msg_header = Optional((2 * Word(alphanums) + 2 * Word(nums) + Suppress(':')).ignore('*' + restOfLine))

		msg_param = []
		msg_content = []
		header_read = False
		for i in range(len(data_file)):
			if len(data_file[i]) <= 1 or data_file[i][0] == '*': continue
			if not header_read:
				msg_param = msg_header.parseString(data_file[i]).asList()
				if len(msg_param) == 0:
					print("Error while parsing the file. Check it again")
					break
				header_read = True
			else:
				if data_file[i] != "end_msg":
					msg_content.append(data_file[i])
				else:
					self.results.append([True, msg_param, '\n'.join(msg_content)])
					msg_content = []
					header_read = False

	def open_file(self, name):
		with open(os.path.join(os.getcwd(), "config/" + name), "r") as myfile:
			return myfile.readlines()

	def get_results(self):
		return self.results

	def parse_append_types(self, parse_type, number_repeted):
		self.setting_types.append([Optional(parse_type.ignore('*' + restOfLine)), number_repeted])

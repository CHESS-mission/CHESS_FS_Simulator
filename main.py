import sys
import subprocess
import time

'''
The purpose of this file is to start others processes necessary for the global operation
'''


class Runner():

	def __init__(self, setting_filename):
		self.run(setting_filename)

	def run(self, setting_filename):
		# start the interface script
		subprocess.call('start venv/Scripts/python.exe interface/interface.py ' + setting_filename, shell=True)


if __name__ == "__main__":
	arg_filename = sys.argv[1]
	Runner(arg_filename)
else:
	# imbedded as a module
	pass

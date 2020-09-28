import os
import sys

sys.path.insert(0, os.path.abspath(os.getcwd()))
import time
import zmq

from core.utils import transmit_msg
from config.parsing import Parser
import subprocess


class interface_core(object):

	def __init__(self, conf_file_name):
		self.list_inter = self.list_boards = []
		self.interface_addr = self.conf_string = ""
		os.system("title " + "INTERFACE")
		self.parser(conf_file_name)
		self.launch_boards()
		self.data_reception()

	def parser(self, filename):
		parsefile = Parser(filename, True).get_results()
		self.list_inter = parsefile[:2]
		self.list_boards = parsefile[2:]
		self.interface_addr = 'tcp://' + str(self.list_inter[0][1]) + ':' + str(self.list_inter[1][1])
		self.conf_string = ''
		for i in range(len(self.list_boards)):
			self.list_boards[i].insert(0,
									   'tcp://' + self.list_inter[0][1] + ':' + str(int(self.list_inter[1][1]) + i + 1))
			self.list_boards[i].insert(1, self.interface_addr)
			self.conf_string += '|'.join(self.list_boards[i]) + '||'
		self.conf_string = self.conf_string[:-2]

	def launch_boards(self):
		for i in range(len(self.list_boards)):
			subprocess.call('start venv/Scripts/python.exe core/board.py' + ' ' + self.list_boards[i][0],
							shell=True)  # parameters are the address of the board
			transmit_msg(self.list_boards[i][0], self.conf_string)
		print("Boards initialized")

	def data_reception(self):
		# create file or erase the existing one for data saving
		file = open("logs/interface_data.txt", "w+")
		file.write('Beginning of the interface log file.\nAll transmitted messages are gathered by the interface. '
				   'Message\'s schema is like the following:\n<Emitter board> to <Receiver board> through <protocol>, '
				   'size=<data size in ko>ko.[CR]<message>[CR]\n\n\n')
		# set receiving socket
		context = zmq.Context()
		socket = context.socket(zmq.PULL)
		socket.bind(self.interface_addr)
		print("Starting data reception...")
		while True:
			msg = socket.recv_pyobj()
			if not msg[0]:  # free mode
				msg = str(msg[1])
				print(msg)
				if msg == 'quit': break
				file.write("*** FREE MODE USED ***\t" + msg + '\n')
			else:  # auto mode
				add_lines = msg[1][0] + ' to ' + msg[1][1] + ' through ' + msg[1][2] + ', size = ' + msg[1][
					3] + 'ko.\n' + msg[2] + '\n\n'
				file.write(add_lines)

		file.close()
		self.exit_prgm()

	def exit_prgm(self):
		for i in range(len(self.list_boards)):
			transmit_msg(self.list_boards[i][0], [False, 'quit'])
		time.sleep(0.05)
		sys.exit(0)

	def run(self):
		pass


if __name__ == "__main__":
	arg_filename = sys.argv[1]
	interface = interface_core(arg_filename)
	interface.run()

import sys
import os

sys.path.insert(0, os.path.abspath(os.getcwd()))
import multiprocessing
import time
import zmq

from config.parsing import Parser
from core.utils import transmit_msg
from collections import Counter


class Board_core(object):

	def __init__(self, address):
		self.name = self.inter_addr = self.protocols = ""
		self.address = address
		self.base_addr = address.rsplit(':', 1)[0] + ':'
		self.ext_addr = address.rsplit(':', 1)[1]
		self.boards_list = []
		self.is_auto_active = False

		self.queue = multiprocessing.Queue()
		proc_recv = multiprocessing.Process(target=self.receiver)
		proc_recv.daemon = True

		proc_recv.start()
		self.init_params()
		proc_file = multiprocessing.Process(target=self.file_manager, args=(self.name,))
		proc_file.start()

	def init_params(self):
		data = str(self.queue.get())
		first_split = data.split('||')
		for i in range(len(first_split)):
			second_split = first_split[i].split('|')
			if second_split[0] == self.address:
				self.inter_addr = second_split[1]
				self.name = second_split[2]
				self.protocols = second_split[3:]
				os.system("title " + self.name)
				print(self.name + ' is set at ' + self.address)
			else:
				self.boards_list.append(second_split)

	def receiver(self):
		context = zmq.Context()
		socket = context.socket(zmq.PULL)
		socket.bind(self.address)
		while True:
			msg = socket.recv_pyobj()
			self.queue.put(msg)
			time.sleep(0.05)

	def file_manager(self, name):
		# create file or erase the existing one for data saving
		file = open("logs/" + name + "_data.txt", "w+")
		file.write('Beginning of the ' + name + ' log file.\nAll received and transmitted messages from this board'
												' are saved in this file.\nMessage\'s schema is like the following:\nIf it is a reception:\n\t'
												'Received MSG from <Emitter board> through <protocol>, size=<data size in ko>ko.[CR]<message>[CR]\n'
												'If it is an emission:\n\tSend MSG to <Receiver board> through <protocol>, size=<data size in ko>ko.[CR]<message>[CR]\n\n\n')
		while True:
			data_to_write = self.queue.get()
			if not data_to_write[0]:  # free mode
				msg = str(data_to_write[1])
				if msg == 'quit':
					break
				elif msg.split(' ', 1)[0] == self.name:
					msg = "*** FREE MODE USED ***\tTX:" + msg + '\n'
				else:
					msg = "*** FREE MODE USED ***\tRX:" + msg + '\n'
				print(msg)
				file.write(msg)
			else:
				if data_to_write[1][0] == name:
					add_lines = 'Send MSG to ' + data_to_write[1][1]
				else:
					add_lines = 'Received MSG from ' + data_to_write[1][0]
				add_lines = add_lines + ' through ' + data_to_write[1][2] + ', size = ' + data_to_write[1][
					3] + 'ko.\n' + data_to_write[2] + '\n\n'
				file.write(add_lines)
		file.close()

	def run(self, fileno):
		sys.stdin = os.fdopen(fileno)  # open stdin in this process
		beg = False
		while True:
			if not beg:
				print("Select the following option for this board (0 to save and quit):\n"
					  "\t1 - Free addressing message operation\n"
					  "\t2 - Automatic addressing message operation (detailed in algo.txt file)")

			choice = input(">")
			try:
				choice_int = int(choice)
			except ValueError:
				choice_int = -1
			if 1 <= choice_int <= 2:
				beg = False
				if choice_int == 1:
					self.free_mode()
				else:
					if not self.is_auto_active:
						self.auto_mode()
						self.is_auto_active = True
					else:
						print('Auto mode is already active')
			else:
				if choice_int == 0:
					transmit_msg(self.inter_addr, [False, 'quit'])
				else:
					print("Wrong entry. Try again")
					beg = True

	def free_mode(self):
		while True:
			value = input("Enter the board name follow by a / and the message to send (0 to return to menu):\n")
			count = Counter(value)
			if count['/'] == 1:
				[name, msg] = value.split('/', 2)
				addr = self.find_port_from_name(str(name).upper())
				if addr == "":
					print("No board with this name found. Try again")
					continue
				data = [False, self.name + " sends MSG: " + msg]
				transmit_msg(addr, data)
				transmit_msg(self.inter_addr, data)
				self.queue.put(data)
			else:
				if value == '0': break
				print("Wrong entry. Try again")

	def auto_mode(self):
		with open("config/algo.txt", "r") as file: data = file.read()
		beg_code = 'start-' + self.name
		idx = data.find(beg_code)
		algo = data[idx + len(beg_code) + 1:data.find('start-', idx + 10)]
		parsed_list = Parser(algo, False).get_results()

		for i in range(len(parsed_list)):
			parsed_list[i][1].insert(0, self.name)
			time_sleep = int(parsed_list[i][1][4])
			parsed_list[i][1].pop(4)
			proc_file = multiprocessing.Process(target=self.auto_mode_process, args=(parsed_list[i], time_sleep))
			proc_file.daemon = True
			proc_file.start()

	def auto_mode_process(self, param_table, delay):
		addr_target = self.find_port_from_name(param_table[1][1])
		if addr_target == "": return
		while True:
			transmit_msg(addr_target, param_table)
			transmit_msg(self.inter_addr, param_table)
			self.queue.put(param_table)
			if delay == 0: break
			time.sleep(delay)

	def find_port_from_name(self, name):
		for i in range(len(self.boards_list)):
			if name == self.boards_list[i][2].upper(): return self.boards_list[i][0]
		return ""


if __name__ == "__main__":
	arg_addr = sys.argv[1]
	board = Board_core(arg_addr)
	fn = sys.stdin.fileno()
	board.run(fn)

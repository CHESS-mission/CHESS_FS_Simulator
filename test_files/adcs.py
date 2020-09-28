import os
from collections import Counter

import zmq
import sys
import time
from multiprocessing import Process

class Adcs_core(object):

    def __init__(self, address, port_tx, port_rx):

        self.addr = address
        self.port_recv = port_rx
        self.port_send = port_tx

    def init_receiver(self):
        print("ADCS-RX: starting receiver socket")

        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(self.addr + self.port_recv)
        print("ADCS-RX: receiver socket settled at " + self.addr + self.port_recv + ". Starting receiving data")
        while True:
            msg = str(socket.recv_string())
            print("ADCS-RX:" + msg)

    def transmit_msg(self, cxt, port, msg):
        socket = cxt.socket(zmq.PUSH)
        socket.connect(self.addr + port)
        socket.send_string(msg)
        print("ADCS-TX: msg %s sent at port %s" % (msg, port))
        socket.close()

    def run(self, fileno):
        context = zmq.Context()
        soc_int = context.socket(zmq.PUSH)
        soc_int.connect(self.addr + "5550")
        sys.stdin = os.fdopen(fileno)  # open stdin in this process
        time.sleep(0.05)
        while True:
            value = input("Enter the ip port follow by a / and the message to send:\n")
            count = Counter(value)
            if count['/'] == 1:
                [port, msg] = value.split('/', 2)
                soc_int.send_string(msg)
                self.transmit_msg(context, port, msg)
            else:
                print("Wrong entry. Try again")

if __name__ == "__main__":
    arg_addr = sys.argv[1]
    arg_port_tx = sys.argv[2]
    arg_port_rx = sys.argv[3]
    fn = sys.stdin.fileno()
    adcs = Adcs_core(arg_addr, arg_port_tx, arg_port_rx)
    Process(target=adcs.init_receiver).start()
    Process(target=adcs.run, args=(fn,)).start()
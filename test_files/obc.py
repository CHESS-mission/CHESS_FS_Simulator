import os
import time
from collections import Counter
import zmq
import sys
from multiprocessing import Process

class Obc_core(object):

    def __init__(self, address):

        self.int_addr = address

    def init_receiver(self):
        print("OBC-RX: starting receiver socket")

        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(self.addr + self.port_recv)
        print("OBC-RX: receiver socket settled at " + self.addr + self.port_recv + ". Starting receiving data")
        while True:
            msg = str(socket.recv_string())
            print("OBC-RX:" + msg)

    def transmit_msg(self, cxt, port, msg):
        socket = cxt.socket(zmq.PUSH)
        socket.connect(self.addr + port)
        socket.send_string(msg)
        print("OBC-TX: msg %s sent at port %s" % (msg, port))
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

# OBC sends msg TODO supprimer
if __name__ == "__main__":
    time.sleep(10)
    #os.system("title " + "ok")
    arg_addr = sys.argv[1]
    fn = sys.stdin.fileno()
    print("ok")
    obc = Obc_core(arg_addr)
    #Process(target=obc.init_receiver).start()
    #Process(target=obc.run, args=(fn,)).start()
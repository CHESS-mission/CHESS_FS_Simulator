import zmq


def transmit_msg(addr, msg):
	cxt = zmq.Context()
	socket = cxt.socket(zmq.PUSH)
	socket.connect(addr)
	socket.send_pyobj(msg)
	socket.close()

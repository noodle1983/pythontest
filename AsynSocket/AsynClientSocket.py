import socket
import errno

STATUS_N = 0
STATUS_C = 1
STATUS_R = 2
STATUS_W = 4

class AsynClientSocket:

	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.status = STATUS_N

	def connect(self, host,	port):
		self.addr = (host, port)
		try:
			self.sock.connect(self.addr)
		except socket.error, e:
			if e.errno in (errno.EINPROGRESS, errno.EWOULDBLOCK):
				print "trying to connect, errno:", e
				return
			else:
				print "raise error:", e
				raise
		self.status = STATUS_C

	def	close(self):
		self.sock.close()
		self.sock.status = STATUS_N

if __name__ == '__main__':
	sock = AsynClientSocket()
	sock.connect('147.128.104.32', 8080)
	raw_input("input any key to quit.")
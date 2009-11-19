import socket
import errno

STATUS_N = 0 #None
STATUS_C = 1 #Connected
STATUS_R = 2 #Reading
STATUS_W = 4 #Writing
STATUS_E = 8 #Error

class CountDowner:

	def __init__(self, begin = 0):
		self.no = begin

	def reset(self, begin):
		self.no = begin

	def decrease(self, cut = 1):
		self.no = self.no - cut

	def done(self):
		return self.no <= 0

class AsynClientSocket:

	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.status = STATUS_N
		self.connect_timeout = CountDowner(3)

	def connect(self, host,	port, timeout = 3):
		self.addr = (host, port)
		self.connect_timeout.reset(timeout) 
		try:
			self.sock.connect(self.addr)
		except socket.error, e:
			if e.errno in (errno.EINPROGRESS, errno.EWOULDBLOCK):
				print "trying to connect, errno:", e
				return
			else:
				print "raise error:", e
				self.status = STATUS_E
				raise
		self.status = STATUS_C

	def close(self):
		self.sock.close()
		self.sock.status = STATUS_N

	def reportError(self):
		print "error occur"
		self.sock.status = STATUS_E
		self.sock.close()
		
	def getFileNo(self):
		return self.sock.fileno()

if __name__ == '__main__':
	import select
	print "-----------------test2-----------------"
	sock = AsynClientSocket()
	try:
		sock.connect('150.236.80.149', 9414)
	except socket.error, e:
		print e
		raw_input("test failed.")
	

	sockfds = []
	sockfds.append(sock.getFileNo())
	(infds, outfds, errfds) = select.select(sockfds, sockfds, sockfds, 1)
	print "infds:", infds
	print "outfds:", outfds
	print "errfds:", errfds
	
	print "-----------------test2-----------------"
	sock = AsynClientSocket()
	try:
		sock.connect('192.168.168.168', 80)
	except socket.error, e:
		print e
		raw_input("test failed.")
	
	import select
	sockfds = []
	sockfds.append(sock.getFileNo())
	(infds, outfds, errfds) = select.select(sockfds, sockfds, sockfds, 1)
	sock.connect_timeout.decrease(1)
	while not infds and not outfds and not errfds and not sock.connect_timeout.done():
		print "1 second eclapse"
		(infds, outfds, errfds) = select.select(sockfds, sockfds, sockfds, 1)
		sock.connect_timeout.decrease(1)
		
	print "infds:", infds
	print "outfds:", outfds
	print "errfds:", errfds
	raw_input("test ok.")

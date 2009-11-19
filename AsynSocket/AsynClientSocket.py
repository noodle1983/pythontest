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

class AsynConnector:

	def __init__(self, theSock):
		self.sock = theSock
		self.countdowner = CountDowner(3)

	def connect(self, addr, timeout):
		self.countdowner.reset(timeout) 
		try:
			self.sock.connect(addr)
		except socket.error, e:
			if e.errno in (errno.EINPROGRESS, errno.EWOULDBLOCK):
				print "connecting to ", addr 
				return False
			else:
				print "raise error:", e
				raise
		return true
	
	def elapse(self, second = 1):
		self.countdowner.decrease(second)

	def hasError(self, sockStatus):
		"""
			return true if status has error flag
			return true if countdowner is done
			return true if status has no connected flag and has read and write flag
		"""
		if self.countdowner.done():
			print "connector timeout." 
			return True
		if (sockStatus & STATUS_E) or (sockStatus == 6):
			print "connector error."
			return True

import threading
class ConStatus:
	def __init__(self, theStatus = STATUS_N):
		self.lock = threading.RLock()
		self.status = theStatus

	def addStatus(self, theStatus):
		with self.lock:
			self.status = self.status | theStatus

	def rmStatus(self, theStatus):
		with self.lock:
			self.status = self.status & ~theStatus

	def set(self, theStatus = STATUS_N):
		with self.lock:
			self.status = theStatus

	def get(self):
		return self.status

class AsynClientSocket:

	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.status = ConStatus()
		self.connector = AsynConnector(self.sock)

	def connect(self, host,	port, timeout = 3):
		self.addr = (host, port)
		self.status.set()
		retCon = False
		try:
			retCon = self.connector.connect(self.addr, timeout)
		except socket.error, e:
			print "raise error:", e
			self.status.addStatus( STATUS_E )
			raise
		if retCon:
			self.status.addStatus(STATUS_C)

	def close(self):
		self.sock.close()
		self.sock.status.set()

	def reportError(self, strerror):
		print "error occur:", strerror
		self.sock.status.set(STATUS_E)
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
	sock.connector.elapse(1)
	while not infds and not outfds and not errfds and not sock.connector.hasError(sock.status.get()):
		print "1 second eclapse"
		(infds, outfds, errfds) = select.select(sockfds, sockfds, sockfds, 1)
		sock.connector.elapse(1)
		
	print "infds:", infds
	print "outfds:", outfds
	print "errfds:", errfds
	raw_input("test ok.")

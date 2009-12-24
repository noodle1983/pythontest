import socket
import errno
from BipBuffer import BipBuffer

import SocketStatus
import CONST

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
		return True
	
	def elapse(self, second = 1):
		self.countdowner.decrease(second)

	def isConnected(self, sockStatus):
		return (sockStatus & CONST.STATUS_C)\
				or ((sockStatus & CONST.STATUS_CONNECTED_MASK) == CONST.STATUS_CONNECTED_CON)

	def hasError(self, sockStatus):
		"""
			return true if status has error flag
			return true if countdowner is done
			return true if status has no connected flag and has read and write flag
		"""
		if self.countdowner.done():
			print "connector timeout." 
			return True
		if (sockStatus & CONST.STATUS_E): 
			print "connector error."
			return True

class AsynClientSocket:

	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.status = SocketStatus.SocketStatus()

		self.connector = AsynConnector(self.sock)

		self.recvBuffer = BipBuffer(1024*1024)
		self.recvBackupPackage = 0
		self.sendBuffer = BipBuffer(1024*1024)

	def setBuffer(self, theRecvBuffer, theSendBuffer):
		self.recvBuffer = theRecvBuffer
		self.sendBuffer = theSendBuffer

	def connect(self, host,	port, timeout = 3):
		self.addr = (host, port)
		self.status.set()
		retCon = self.connector.connect(self.addr, timeout)
		if retCon:
			self.status.addStatus(CONST.STATUS_C)

	def checkConnectedEvent(self):
		if not self.connector.isConnected(self.status.get()):
			if self.connector.hasError(self.status.get()):
				self.reportError("connecting error!\n")
		elif not (self.status.get()& CONST.STATUS_C):
			self.status.addStatus(CONST.STATUS_C)
			return True
		return False

	def close(self):
		self.sock.close()
		
	def reportError(self, strerror):
		"AsynClientSocket::reportError"

		print "error occur:", strerror
		self.status.addStatus(CONST.STATUS_E)
		self.status.rmStatus(CONST.STATUS_EF)
		self.sock.close()
		
	def getFileNo(self):
		return self.sock.fileno()

	def send(self, package, len):
		self.sendBuffer.write(package, len)
		self.status.addStatus(CONST.STATUS_D)

	def sendImpl(self):
		"AsynClientSocket.sendImpl"
		try:
			while True:
				(package, len) = self.sendBuffer.read_reserve()	
				if len <= 0:
					break
				sendedLen = self.sock.send(package)
				self.sendBuffer.read_confirm(sendedLen)
		except socket.error, e:
			self.reportError("sending error!\n" + str(e))
			return
		finally:
			self.status.rmStatus(CONST.STATUS_WF|CONST.STATUS_D)	
			
	def recv(self):
		return self.recvBuffer.read()

	def recvImpl(self):
		"AsynClientSocket::recvImpl"

		buf = ""
		recvLen = 0
		try:
			if self.recvBackupPackage:
				buf = self.recvBackupPackage
				self.recvBackupPackage = 0
			else:
				buf = self.sock.recv(4096)
				self.status.rmStatus(CONST.STATUS_RF)	
			recvLen = len(buf)
			if recvLen <= 0:
				self.reportError("recv None buffer")
				return
			self.recvBuffer.write(buf, recvLen)
		except socket.error, e:
			if e.errno == errno.ENOBUFS:
				self.recvBackupPackage = buf 
				self.status.addStatus(CONST.STATUS_RF)	
			self.reportError("receiving error!\n" + str(e))
			return

	def dump(self):
		return self.status.dump()

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

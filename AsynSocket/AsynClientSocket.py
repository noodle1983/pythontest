import socket
import threading
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

	def connect(self, addr, timeout):
		try:
			self.sock.connect(addr)
		except socket.error, e:
			if e.errno in (errno.EINPROGRESS, errno.EWOULDBLOCK):
				print "[AsynConnector.connect]connecting to ", addr 
				return False
			else:
				print "[AsynConnector.connect]exception:", e
				raise
		return True
	
	def isConnected(self, sockStatus):
		return (sockStatus & CONST.STATUS_C)\
				or ((sockStatus & CONST.STATUS_CONNECTED_MASK) == CONST.STATUS_CONNECTED_CON)

	def hasError(self, sockStatus):
		"""
			return true if status has error flag
			return true if countdowner is done
			return true if status has no connected flag and has read and write flag
		"""
		if (sockStatus & CONST.STATUS_E): 
			print "[AsynConnector.hasError]connector error."
			return True

class AsynClientSocket:

	def __init__(self):
		self.initSock()

		self.connector = AsynConnector(self.sock)
		self.connectTimer = threading.Timer(5, self.handleConnectTimeout)

		self.recvBuffer = BipBuffer(1024*1024)
		self.recvBackupPackage = 0
		self.sendBuffer = BipBuffer(1024*1024)

	def initSock(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.status = SocketStatus.SocketStatus()

	def setBuffer(self, theRecvBuffer, theSendBuffer):
		self.recvBuffer = theRecvBuffer
		self.sendBuffer = theSendBuffer

	def connect(self, host,	port, timeout = 3):
		if self.status.has(CONST.STATUS_C):
			print "[AsynClientSocket.connect]ignore request! connected to ", self.addr
			return
		self.addr = (host, port)
		self.status.set()
		retCon = self.connector.connect(self.addr, timeout)
		if retCon:
			self.status.addStatus(CONST.STATUS_C)
		else:
			self.connectTimer.start()

	def handleConnected(self):
		self.connectTimer.cancel()

	def handleConnectTimeout(self):
		print "[AsynClientSocket.handleConnectTimeout]", self.addr
		self.status.addStatus(CONST.STATUS_RF)

	def checkConnectedEvent(self):
		if not self.connector.isConnected(self.status.get()):
			if self.connector.hasError(self.status.get()):
				self.reportError("[AsynClientSocket.checkConnectedEvent]connecting error!\n")
		elif not (self.status.get()& CONST.STATUS_C):
			self.status.addStatus(CONST.STATUS_C)
			return True
		return False

	def close(self):
		try:
			self.sock.close()
		except Exception, e:
			print "[AsynClientSocket.close]", e	
		finally:
			self.status.addStatus(CONST.STATUS_E|CONST.STATUS_UD)
			self.status.rmStatus(CONST.STATUS_C)


	def reportError(self, strerror):
		"AsynClientSocket::reportError"

		print strerror
		self.connectTimer.cancel()
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
			if e.errno in (errno.EINPROGRESS, errno.EWOULDBLOCK):
				return
			print "[AsynClientSocket.sendImpl]sending error!" + str(e)
			raise e
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
				raise socket.error(errno.ENOBUFS, "AsynClientSocket.recvImpl", "Buffer has not enough space to write")
			self.recvBuffer.write(buf, recvLen)
		except socket.error, e:
			if e.errno == errno.ENOBUFS:
				self.recvBackupPackage = buf 
				self.status.addStatus(CONST.STATUS_RF)	
			elif e.errno in (errno.EINPROGRESS, errno.EWOULDBLOCK):
				return
			else:
				raise e
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

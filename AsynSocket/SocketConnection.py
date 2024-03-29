from AsynClientSocket import AsynClientSocket
from BipBuffer import BipBuffer
import threading
import socket
import errno
from Bind import Bind1

import SocketStatus
import CONST

class SocketConnection:
	"""
	generate socket jobs
	notify protocol layer with incoming data
	"""
	def __init__(self, theSocket, theProtocol, theProcessor):
		"""
		theSocket: socket facade
		theProtocol: socket event handler
		theProcessor: thread facade
		"""
		self.recvBuffer = BipBuffer(1024*1024)
		self.recvBuffer.setMaxRead(4096)
		self.sendBuffer = BipBuffer(1024*1024)
		self.recvBuffer.setMaxRead(4096)
		self.sendLock = threading.RLock()

		self.sock = theSocket
		self.sock.setBuffer(self.recvBuffer, self.sendBuffer)
		self.fd = theSocket.getFileNo()
		self.status = theSocket.status
		self.addr = ('', 0)

		self.proto = theProtocol
		#self.proto.addConnection(self)
		self.processor = theProcessor
		self.protoHandleConnected = Bind1(self.proto.handleConnected, self)
		self.protoHandleInput = Bind1(self.proto.handleInput, self)

	def hasDataToSend(self):
		return self.sendBuffer.dataLen() > 0

	def isConnected(self):
		return self.status.has(CONST.STATUS_C)

	def dump(self):
		return "[sock]%s\n[sendBuffer]%s\n[recvBuffer]%s\n"%\
				(str(self.sock.dump()), str(self.sendBuffer.dump()), str(self.recvBuffer.dump()))

	def reportError(self, strError = ""): 
		self.sock.reportError(strError)
		self.proto.handleError(self, strError)

	def connect(self, host, port):
		try:
			self.sock.connect(host, port)
			self.addr = (host, port)
			#duplicate when genJobs
			#if self.sock.status.has(CONST.STATUS_C):
			#	self.handleConnected()
		except socket.error, e:
			self.reportError("[SocketConnection.connect]connecting error:" + str(e))
	
	def handleConnected(self):
		print "[SocketConnection.handleConnected]"
		self.sock.handleConnected()
		self.sendBuffer.reset()
		self.recvBuffer.reset()
		self.processor.process(self.fd, self.protoHandleConnected)

	def close(self):
		try:
			self.protoHandleConnected = None
			self.protoHandleInput = None
			self.sock.close()
			self.proto.handleClose(self)
		except socket.error, e:
			self.reportError("[SocketConnection.close]close error:" + str(e))

	def send(self, package, len):
		if not self.status.has(CONST.STATUS_C):
			raise socket.error(errno.EBADF, "SocketConnection.send", "not connected!")	
		with self.sendLock:
			self.sendBuffer.write(package, len)
		#self.status.addStatus(CONST.STATUS_D)
	
	def sendImpl(self):
		if not self.status.has(CONST.STATUS_C):
			print "SocketConnection.sendImpl", "not connected!"
		try:
			self.sock.sendImpl()
		except:
			self.reportError("[SocketConnection.sendImpl]send error!") 

	def readRecvBuffer(self):
		try:
			return self.recvBuffer.read()
		except socket.error, e:
			self.reportError("[SocketConnection.readRecvBuffer]" + str(e)) 

	def preReadRecvBuffer(self):
		try:
			return self.recvBuffer.read_reserve()
		except socket.error, e:
			self.reportError("[SocketConnection.preReadRecvBuffer]" + str(e)) 
	
	def cnfmPreReadRecvBuffer(self, cnfmLen):
		try:
			return self.recvBuffer.read_confirm(cnfmLen)
		except socket.error, e:
			self.reportError("[SocketConnection.confirmPreReadRecvBuffer]" + str(e)) 

	def recvImpl(self):
		"SocketConnection.recvImpl"
		try:
			self.sock.recvImpl()
			self.processor.process(self.fd + 1, self.protoHandleInput)
		except socket.error, e:
			self.reportError("[SocketConnection.recvImpl]" + str(e)) 

	def getFd(self):
		try:
			return self.sock.getFileNo()
		except socket.error, e:
			self.reportError("[SocketConnection.getFd]bad file descriptor:" + str(e))
			return 0
	
	def genJobs(self):
		#print "[SocketConnection.genJobs]", self.sock.dump()
		if self.sock.status.has(CONST.STATUS_EF):
			self.reportError("[SocketConnection.genJobs]socket error!")

		if self.sock.status.has(CONST.STATUS_UD | CONST.STATUS_E): 
			return

		if not self.sock.status.has(CONST.STATUS_C):
			if self.sock.connector.hasError(self.status.get()):
				self.reportError("[SocketConnection.genJobs]connecting error!")
				return
			if self.sock.connector.isConnected(self.status.get()):
				print "[SocketConnection.genJobs]", self.sock.dump()
				self.status.addStatus(CONST.STATUS_C)
				self.handleConnected()

		if self.sock.status.has(CONST.STATUS_RF):
			self.processor.process(self.fd + 2, self.recvImpl)
		elif self.sock.recvBuffer.dataLen() > 0:
			self.processor.process(self.fd + 1, self.protoHandleInput)

		if self.sock.status.has(CONST.STATUS_WF) and self.hasDataToSend():
			self.processor.process(self.fd + 3, self.sendImpl)



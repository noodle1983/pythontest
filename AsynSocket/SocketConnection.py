from AsynClientSocket import AsynClientSocket
from BipBuffer import BipBuffer
import threading
import socket
import errno

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
		self.sendBuffer = BipBuffer(1024*1024)
		self.sendLock = threading.RLock()

		self.sock = theSocket
		self.sock.setBuffer(self.recvBuffer, self.sendBuffer)
		self.fd = theSocket.getFileNo()
		self.status = theSocket.status

		self.proto = theProtocol
		self.processor = theProcessor

	def reportError(self, strError = ""): 
		self.sock.reportError(strError)
		self.proto.handleError(strError)

	def connect(self, addr, port):
		try:
			self.sock.connect(addr, port)
			if self.sock.status.has(CONST.STATUS_C):
				self.handleConnected()
		except socket.error, e:
			self.reportError("[SocketConnection.connect]connecting error:" + str(e))
	
	def handleConnected(self):
		self.sock.handleConnected()
		self.sendBuffer.reset()
		self.recvBuffer.reset()
		self.processor.process(self.fd, self.proto.handleConnected)

	def close(self):
		try:
			self.sock.close()
			self.proto.close()
		except socket.error, e:
			self.reportError("[SocketConnection.close]close error:\n" + str(e))

	def send(self, package, len):
		if not self.status.has(CONST.STATUS_C):
			raise socket.error(errno.EBADF, "SocketConnection.send", "not connected!")	
		with self.sendLock:
			self.sendBuffer.write(package, len)
		self.status.addStatus(CONST.STATUS_D)
	
	def sendImpl(self):
		try:
			self.sock.sendImpl()
		except socket.error, e:
			self.reportError("[SocketConnection.sendImpl]send error!") 
	
	def recvImpl(self):
		"SocketConnection.recvImpl"
		try:
			self.sock.recvImpl()
			self.processor.process(self.fd + 3, self.proto.handleInput)
		except socket.error, e:
			self.reportError("[SocketConnection.recvImpl]recv error!") 

	def getFd(self):
		try:
			return self.sock.getFileNo()
		except:
			self.reportError("[SocketConnection.getFd]bad file descriptor:" + str(e))
			return 0
	
	def genJobs(self):
		print "[SocketConnection.genJobs]", self.sock.dump()
		if not self.sock.status.has(CONST.STATUS_C):
			if self.sock.connector.hasError(self.status.get()):
				self.reportError("[SocketConnection.genJobs]connecting error!\n")
				return
			if self.sock.connector.isConnected(self.status.get()):
				self.status.addStatus(CONST.STATUS_C)
				self.handleConnected()

		if self.sock.status.has(CONST.STATUS_EF):
			self.reportError("[SocketConnection.genJobs]socket error!\n")

		if self.sock.status.has(CONST.STATUS_UD | CONST.STATUS_E): 
			return
		if self.sock.status.has(CONST.STATUS_RF):
			self.processor.process(self.fd + 1, self.recvImpl)
		if self.sock.status.has(CONST.STATUS_WF) and self.sock.status.has(CONST.STATUS_D):
			self.processor.process(self.fd + 2, self.sock.sendImpl)



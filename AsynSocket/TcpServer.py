#/usr/local/bin/python
import socket
import errno
import threading
import SocketStatus
import CONST
from AsynClientSocket import AsynClientSocket
from SocketConnection import SocketConnection
from ConnectionManager import ConnectionManager
from Bind import Bind1

class TcpServer:
	"""
	interface:
		reportError(self, str)
		status
		close
		genJobs
	"""
	def __init__(self, theProtocol, theProcessor):
		self.processor = theProcessor
		self.connectionMan = ConnectionManager()
		self.status = SocketStatus.SocketStatus()
		self.status.addStatus(CONST.STATUS_C)

		self.proto = theProtocol

	def startAt(self, port): 
		print "[TcpServer.startAt]", port
		try:
			self.port = port
			self.addr = ('*', port)
			self.connectionMan.start()
			self.init()
		except Exception, e:
			self.reportError("[TcpServer.startAt]" + str(e)) 
			return


	def init(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(('', self.port))
		self.sock.listen(20000)
		self.sock.setblocking(0)
		#self.sock.settimeout(3)
		self.connectionMan.addConnection(self.sock.fileno(), self)

	def getFd(self):
		try:
			return self.sock.fileno()
		except Exception, e:
			self.reportError("[TcpServer.getFd]" + str(e)) 
			return 0

	def accept(self):
		try:
			sock, addr = self.sock.accept()
			newSock = AsynClientSocket()
			newSock.changeToServerConnection(sock)

			connection = SocketConnection(newSock, self.proto, self.processor)
			connection.addr = addr
			self.connectionMan.addConnection(newSock.getFileNo(), connection)

			self.protoHandleConnected = Bind1(self.proto.handleConnected, self)
			self.processor.process(connection.getFd(), Bind1(self.proto.handleConnected, connection))

		except Exception, e:
			if e.errno in (errno.EINPROGRESS, errno.EWOULDBLOCK):
				return
			self.reportError("[TcpServer.accept]" + str(e))
			return
		finally:
			self.status.rmStatus(CONST.STATUS_RF)	


	def close(self):
		if not self.status.has(CONST.STATUS_C):
			return
		self.status.addStatus(CONST.STATUS_E|CONST.STATUS_UD)
		self.status.rmStatus(CONST.STATUS_C|CONST.STATUS_EF)
		self.sock.close()
		self.connectionMan.stop()
		self.proto.handleClose(self)

	def restart(self, port = 0):
		self.close()
		if port != 0:
			self.port = port
		self.startAt(self.port)

	def genJobs(self):
		#print "[TcpServer.genJobs]", self.status.dump()
		if self.status.has(CONST.STATUS_EF):
			self.reportError("[TcpServer.genJobs]socket error!\n")

		if self.status.has(CONST.STATUS_UD | CONST.STATUS_E)\
				or not self.status.has(CONST.STATUS_C): 
			return

		if self.status.has(CONST.STATUS_RF):
			self.processor.process(self.getFd() + 1, self.accept)

	def reportError(self, strError = ""): 
		self.proto.handleError(self, strError)
		self.close()
	

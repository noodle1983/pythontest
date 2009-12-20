from AsynClientSocket import AsynClientSocket

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
		self.sock = theSocket
		self.fd = theSocket.getFileNo()
		self.proto = theProtocol
		self.prcssr = theProcessor

	def checkConnected(self):	
		if (self.sock.checkConnected()):
			theProcessor.process(self.fd, self.proto.OnConnected)

	def reportError(self, strError): 
		self.sock.reportError(strError)
		self.proto.OnError(strError)

	def connect(self, addr, port):
		try:
			self.sock.connect(addr, port)
		except socket.error, e:
			self.reportError("connecting error:\n" + str(e))

	def getFd(self)
		try:
			return self.sock.getFileNo()
		except:
			self.reportError("bad file descriptor:\n" + str(e))
			return 0



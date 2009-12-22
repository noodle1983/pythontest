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
		self.status = theSocket.status
		self.close = theSocket.close

		self.proto = theProtocol
		self.processor = theProcessor

	def checkConnected(self):	
		if (self.sock.checkConnected()):
			theProcessor.process(self.fd, self.proto.handleConnected)

	def reportError(self, strError = ""): 
		self.sock.reportError(strError)
		self.proto.handleError(strError)

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
	
	def genJobs(self):
		if sock.status.has(CONST.STATUS_EF):
			self.processor.process(self.fd, self.reportError)
		if sock.status.has(CONST.STATUS_UD | CONST.STATUS_E): 
			continue
		if sock.status.has(CONST.STATUS_RF):
			self.processor.processList(self.fd + 1, [self.sock.recvImpl, self.proto.handleInput])
		if sock.status.has(CONST.STATUS_WF) and sock.status.has(CONST.STATUS_D):
			self.processor.process(self.fd + 2, self.sock.sendImpl)



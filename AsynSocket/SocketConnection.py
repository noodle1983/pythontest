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
		self.recvBuffer = BipBuffer(1024*1024)
		self.sendBuffer = BipBuffer(1024*1024)

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
				theProcessor.process(self.fd, self.proto.handleConnected)
		except socket.error, e:
			self.reportError("connecting error:\n" + str(e))

	def close(self):
		try:
			self.sock.close()
			self.proto.close()
		except socket.error, e:
			self.reportError("close error:\n" + str(e))

	def send(self, package, len):
		self.sendBuffer.write(package, len)
		self.status.addStatus(CONST.STATUS_D)
	
	def sendImpl(self):
		try:
			self.sock.sendImpl()
		except socket.error, e:
			self.reportError("send error!") 
	
	def recvImpl(self):
		try:
			self.sock.recvImpl()
		except socket.error, e:
			self.reportError("recv error!") 

	def getFd(self)
		try:
			return self.sock.getFileNo()
		except:
			self.reportError("bad file descriptor:\n" + str(e))
			return 0
	
	def genJobs(self):
		if not self.sock.status.has(CONST.STATUS_C):
			if self.sock.connector.hasError(self.status.get()):
				self.reportError("connecting error!\n")
				return
			if self.sock.connector.isConnected(self.status.get()):
				self.status.addStatus(CONST.STATUS_C)
				theProcessor.process(self.fd, self.proto.handleConnected)

		if sock.status.has(CONST.STATUS_EF):
			self.reportError("socket error!\n")

		if sock.status.has(CONST.STATUS_UD | CONST.STATUS_E): 
			return
		if sock.status.has(CONST.STATUS_RF):
			self.processor.processList(self.fd + 1, [self.recvImpl, self.proto.handleInput])
		if sock.status.has(CONST.STATUS_WF) and sock.status.has(CONST.STATUS_D):
			self.processor.process(self.fd + 2, self.sock.sendImpl)



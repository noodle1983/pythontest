import threading
from select import select

class SockSniffer:
	
	def __init__(self, logger, selectProcessor, feProcessor):
		self._logger = logger
		self._inHandlers = {}
		self._outHandlers = {}
		self._errHandlers = {}
		self._lock = threading.RLock()
		self._selectProcessor = selectProcessor
		self._feProcessor

	def unregistSock(self, sock):
		with self._lock:
			self._inHandlers.remove(sock.fileno())
			self._outHandlers.remove(sock.fileno())
			self._errHandlers.remove(sock.fileno())

	def registSock(self, sock, inHandler, outHandler, errHandler):
		with self._lock:
			if inHandler:
				self._inHandlers[sock.fileno()] = (sock, inHandler)
			if outHandler:
				self._outHandlers[sock.fileno()] = (sock, outHandler)
			if errHandler:
				self._errHandlers[sock.fileno()] = (sock, errHandler)

	def run(self):
		with self._lock:
			inFds = self._inHandlers.keys()
			outFds = self._outHandlers.keys()
			errFds = self._errHandlers.keys()
		(inReadyFds, outReadyFds, errReadyFds) = select.select(inFds, outFds, errFds, 1)
		actionList = []	
		with self._lock:
			for fd in errReadyFds:
				sock, errHandler = self._errHandlers.pop(fd)
				actionList.append(errHandler)
			for fd in outReadyFds:
				sock, outHandler = self._outHandlers.pop(fd)
				actionList.append(outHandler)
			for fd in inReadyFds:
				sock, inHandler = self._inHandlers.pop(fd)
				actionList.append(inHandler)
		self.process(actionList)
		self._selectProcessor.process(self.run)


			

		

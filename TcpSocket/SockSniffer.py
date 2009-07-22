import threading
import select
import time

class SockSniffer:
	
	def __init__(self, logger, selectProcessor, feProcessor):
		self._logger = logger
		self._inHandlers = {}
		self._outHandlers = {}
		self._errHandlers = {}
		self._lock = threading.RLock()
		self._selectProcessor = selectProcessor
		self._feProcessor = feProcessor

	def start(self):
		self._logger.debug("[start]")
		self._selectProcessor.process(self.select)
		
	def unregistSock(self, sock):
		with self._lock:
			self._inHandlers.remove(sock.fileno())
			self._outHandlers.remove(sock.fileno())
			self._errHandlers.remove(sock.fileno())

	def registSock(self, sock, inHandler, outHandler, errHandler):
		self._logger.debug(("[registSock]" , sock.fileno()))
		with self._lock:
			if inHandler:
				self._inHandlers[sock.fileno()] = (sock, inHandler)
			if outHandler:
				self._outHandlers[sock.fileno()] = (sock, outHandler)
			if errHandler:
				self._errHandlers[sock.fileno()] = (sock, errHandler)

	def select(self):
		with self._lock:
			inFds = self._inHandlers.keys()
			outFds = self._outHandlers.keys()
			errFds = self._errHandlers.keys()
		try:
			(inReadyFds, outReadyFds, errReadyFds) = select.select(inFds, outFds, errFds, 1)
		except select.error:
			return self._selectProcessor.process(self.select)

		if (not inReadyFds) and (not outReadyFds) and (not errReadyFds):
			return self._selectProcessor.process(self.select)

		self._logger.debug("[select]in:%s, out:%s, err:%s" % (inReadyFds, outReadyFds, errReadyFds))
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
		self._feProcessor.processList(actionList)
		self._selectProcessor.process(self.select)

if __name__ == '__main__' :
	import sys
	import os
	sys.path.append(os.getcwd() + '/../../')
	sys.path.append(os.getcwd() + '/../')
	sys.path.append(os.getcwd() + '/')
	import Logger.logger as Logger
	from processor.Processor import Processor
	selectProcssor = Processor()
	selectProcssor.start()
	feProcessor = Processor(3)
	feProcessor.start()
	log = Logger.Logger()
	sniffer = SockSniffer(log, selectProcssor, feProcessor)
	sniffer.start()

	from TcpServer import TcpServer
	import ConnectionPool as cp
	tcpServer = TcpServer(logger = log, sniffer=sniffer)
	tcpServer.startAt('4080')
	
			

		

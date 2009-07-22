#/usr/local/bin/python
import socket
import threading
import string

import sys
import os
sys.path.append(os.getcwd() + '/../')
from processor.Processor import Processor
from ConnectionPool import ConnectionPool
from Connection import Connection
import Logger.logger as Logger

class TcpServer:
	def __init__(self, logger, protocol = None, connectionPool = None\
	, sniffer = None):
		self._logger = logger 
		if connectionPool:
			self._connectionPool = connectionPool
		else:
			self._connectionPool = ConnectionPool(logger)

		self._protocol = protocol
		self._status = 'running'
		self._sniffer = sniffer
		self._processor = Processor()

	def startAt(self, port): 
		self._logger.debug("start at:" + port)
		self._port = string.atoi(port)

		self.init()
		if self._sniffer is None:	
			#self._thread = threading.Thread(target=self.run)
			#self._thread.start()
			self._processor.start()
			self._processor.process(self.run)
		else:
			self._sniffer.registSock(self._socket, self.run, None, self.shutdown)


	def init(self):
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.bind(('', self._port))
		self._socket.listen(10)
		self._socket.settimeout(1)

	def run(self):
		while self._status == 'running':
			try:
				sock, addr = self._socket.accept()
				con = Connection(logger=self._logger, sock=sock, addr=addr, sniffer=None)
				self._logger.debug("new connection from :" + str(addr))
				self._connectionPool.append(addr, con)	
			except  socket.timeout :
				if self._sniffer:
					return self._sniffer.registSock(self._socket, self.run, None, self.shutdown)
			except  socket.error:
				self.shutdown()
				break

		self._logger.debug("[run]Server Stop!")

	def shutdown(self):
		self._logger.debug("[shutdown]...")
		self._status = 'stop'
		self._socket.close()
		self._processor.stop()
		self._logger.debug("[shutdown]!")

	def restart(self, port):
		self._logger.debug("[restart]...")
		self.shutdown()
		self.startAt(self._port)

if __name__ == "__main__":
	tcpServer = TcpServer(Logger.Logger())
	tcpServer.startAt('4080')
	import time 
	while True:
		time.sleep(20)

	tcpServer.shutdown()


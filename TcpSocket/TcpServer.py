#/usr/local/bin/python
import socket
import threading
import string
from Connection import Connection

class TcpServer:
	def __init__(self, logger, protocol, connectionPool):
		self._logger = logger 
		self._connectionPool = connectionPool
		self._protocol = protocol
		self._status = 'running'

	def startAt(self, port): 
		self._logger.info("start at:" + port)
		self._port = string.atoi(port)

		self.init()
		
		self._thread = threading.Thread(target=self.run)
		self._thread.start()

	def init(self):
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.bind(('', self._port))
		self._socket.listen(10)
		self._socket.settimeout(1)

	def run(self):
		while self._status == 'running':
			try:
				sock, addr = self._socket.accept()
				con = Connection(self._logger, sock, addr)
				self._logger.debug("new connection from :" + str(addr))
				self._connectionPool.append(addr, con)	
			except  socket.timeout :
				pass

		self._logger.debug("[run]Server Stop!")

	def shutdown(self):
		self._logger.debug("[shutdown]...")
		self._status = 'stop'
		self._connectionPool.shutdown()
		self._thread.join()
		self._socket.close()
		self._logger.debug("[shutdown]!")

	def restart(self, port):
		pass

if __name__ == "__main__":
	import sys
	import os
	sys.path.append(os.getcwd() + '/../../')
	sys.path.append(os.getcwd() + '/../')
	sys.path.append(os.getcwd() + '/')
	import Logger.logger as logger
	import ConnectionPool as cp
	log = logger.getLogger()
	tcpServer = TcpServer(log, None, cp.ConnectionPool(log))
	tcpServer.startAt('4080')
	import time 
	while True:
		time.sleep(20)

	tcpServer.shutdown()


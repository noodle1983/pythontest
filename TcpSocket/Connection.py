#!/usr/local/bin/python
import threading
import socket
import time

class Connection:
	
	def __init__(self, logger, sock = None, addr = None, status = 'started'):
		self._status = status
		self._lock = threading.RLock()
		self._sock = sock		
		self._logger = logger
		self._addr = addr
		if self._sock:
			self._sock.settimeout(1)
		self._thread = threading.Thread(target=self.read)
		self._thread.start()

	def connect(self, host, port):
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._addr = (host, port)
		self._sock.connect(self._addr)
		self._status = 'started'	
		self._sock.settimeout(1)

	def stop(self):
		self._status = 'stoped'
		self._sock.close()
		
	def read(self):
		while True:
			try:
				if self._status == 'started' and self._sock is not None:
					buf = self._sock.recv(1024)
					self._logger.info(buf)
					self.write(buf)
				time.sleep(1)
			except socket.timeout:
				pass
		print "recv done"



	def write(self, buf):
		self._sock.send(buf)


	def shutdown(self):
		self._logger.debug("[shutdown]" + str(self._addr) + "...")
		with self._lock:
			self._sock.close()
			self._status = 'stop'
		self._logger.debug("[shutdown]" + str(self._addr) + "!")


if __name__ == '__main__':
	import sys
	import os
	sys.path.append(os.getcwd() + '/../../')
	sys.path.append(os.getcwd() + '/../')
	sys.path.append(os.getcwd() + '/')
	import Logger.logger as logger

	con = Connection(logger.getLogger())
	con.connect('localhost', 4080)
	con.write("hello world!")
	time.sleep(10)

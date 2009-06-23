#!/usr/local/bin/python
import threading

class Connection:
	
	def __init__(self, logger, sock, addr):
		self._status = 'running'
		self._lock = threading.RLock()
		self._sock = sock		
		self._logger = logger
		self._addr = addr

	def onRead(self):
		pass

	def onWrite():
		pass

	def shutdown(self):
		self._logger.debug("[shutdown]" + str(self._addr) + "...")
		with self._lock:
			self._sock.close()
			self._status = 'stop'
		self._logger.debug("[shutdown]" + str(self._addr) + "!")

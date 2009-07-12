#/usr/local/bin/python
import threading
import time

class ConnectionPool:
	
	def __init__(self, logger):
		self._connections = {} 
		self._logger = logger
		self._status = 'running'
		self._thread = threading.Thread(target=self.clean)
		self._thread.start()
	
	def append(self, addr, connection):
		self._logger.debug('[append]' + str(addr))
		con = self._connections.get(addr)
		if con is None :
			self._connections[addr] = connection
		elif con._status == 'stop':
			with con._lock:
				self._connections[addr] = connection
		else:
			logger.warning('[append]ignore new connection:' + str(addr)	)

	def shutdown(self):
		self._logger.debug('[shutdown]...')
		for con in self._connections.values():
			con.shutdown()
		self._status = 'stop'
		self._thread.join()
		self._logger.debug('[ConnectionPool::shutdown]!')


	def clean(self):
		while self._status != 'stop':
			self._connections = dict([(k, v) for (k, v) in self._connections.items() if v._status == 'stopped'])
			time.sleep(1)	

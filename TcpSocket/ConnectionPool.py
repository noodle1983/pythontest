#/usr/local/bin/python
import threading
import time

class ConnectionPool:
	
	def __init__(self, logger):
		self._connections = {} 
		self._logger = logger
		self._status = 'running'
		self._size = 0
		self._thread = threading.Thread(target=self.clean)
		self._thread.start()
	
	def append(self, addr, connection):
		self._logger.debug('[append]' + str(addr))
		con = self._connections.get(addr)
		if con is None :
			self._connections[addr] = connection
		elif con._status == 'stopped':
			with con._lock:
				self._connections[addr] = connection
		else:
			self._logger.warning('[append]ignore new connection:' + str(addr)	)
		self._size = len(self._connections)
		self._logger.debug('[append]pool sizes appended:%d'% self._size)

	def shutdown(self):
		self._logger.debug('[shutdown]...')
		for con in self._connections.values():
			con.shutdown()
		self._status = 'stop'
		self._thread.join()
		self._logger.debug('[ConnectionPool::shutdown]!')


	def clean(self):
		while self._status != 'stop':
			self._connections = dict([(k, v) for (k, v) in self._connections.items() if v._status != 'stopped'])
			if self._size != len(self._connections):
				self._size = len(self._connections)
				self._logger.debug('[clean]pool sizes after clean:%d'% self._size)
			time.sleep(1)	

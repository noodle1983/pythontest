from ConnectionPool import ConnectionPool
import threading
from select import select

class Receiver:
	
	def __init__(self, logger, connectionPool, processors):
		self._logger = logger
		self._connectionPool = connectionPool
		self._thread = threading.Thread(target = self.run)
		self._status = 'idle'
		self._processors = processors
		self._thread.start()

	def run(self):
		self._status = 'running'
		while self._status == 'running':
			readList, writeList, errorList = select(self._connectionPool.getReadList(), None, self._connectionPool.getReadList(), 1)	
			for sock in readList:
				con = self._connectionPool[sock]
				con._status = 'reading'
				self._processors.process(con.onRead)

			for sock in errorList:
				
	def 

			

		

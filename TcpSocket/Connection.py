#!/usr/local/bin/python
import threading
import socket
import time
import array

import sys
import os
sys.path.append(os.getcwd() + '/../')
from processor.Processor import Processor
import Logger.logger as logger

class Connection:
	
	def __init__(self, logger = logger.Logger(), sock = None, addr = None, status = 'started', sniffer = None):
		self._status = status
		self._sock = sock		
		self._logger = logger
		self._addr = addr
		self._sniffer = sniffer
		self._wlock = threading.RLock()
		self._writeQueue = []
		self._readProcessor = Processor()
		self._writeProcessor = Processor()

		if self._sock:
			self._sock.settimeout(1)
			self.__startToHandleMsg()	

		#self._thread = threading.Thread(target=self.read)
		#self._thread.start()

	def __startToHandleMsg(self):
		if self._sniffer:
			self._sniffer.registSock(self._sock, self.read, self.writeImpl, self.shutdown)
		else:
			self._readProcessor.start()
			self._readProcessor.process(self.read)
			self._writeProcessor.start()
			self._writeProcessor.process(self.writeImpl)

	def connect(self, host, port):
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._addr = (host, port)
		self._sock.connect(self._addr)
		self._status = 'started'	
		self._sock.settimeout(1)
		self.__startToHandleMsg()

	def stop(self):
		self._status = 'stopped'
		self._sock.close()
		
	def read(self):
		while self._status != 'stopped':
			try:
				if self._sock is not None:
					buf = self._sock.recv(1024)
					self._logger.debug("[read]bufLen:%d" % len(buf))
					self.write(buf)
			except socket.timeout:
				if self._sniffer:
					return self._sniffer.registSock(self._sock, self.read, None, None)
			except socket.error:
				return self.shutdown()

		print "recv done"

	def write(self, buf):
		with self._wlock:
			self._writeQueue.append(buf)

	def writeImpl(self):
		while self._status != 'stopped':
			with self._wlock: 
				if len(self._writeQueue) > 0: 
					buf = self._writeQueue.pop(0)
					self.__send(buf)	
				else:
					if self._sniffer:
						return self._sniffer.registSock(self._sock, None, self.writeImpl, None)
					time.sleep(1)	

	def __send(self, buf):
		try:
			self._sock.send(buf)
		except socket.error:
			return self.shutdown()

	def shutdown(self):
		self._logger.debug("[shutdown]" + str(self._addr) + "...")
		self._sock.close()
		self._readProcessor.stop()
		self._writeProcessor.stop()
		self._status = 'stopped'
		self._logger.debug("[shutdown]" + str(self._addr) + "!")


if __name__ == '__main__':
	import sys
	import os
	sys.path.append(os.getcwd() + '/../../')
	sys.path.append(os.getcwd() + '/../')
	sys.path.append(os.getcwd() + '/')
	import Logger.logger as logger
	import NetworkObj

	con = Connection(logger.Logger())
	con.connect('localhost', 4080)
	data = array.array('c', '0' * 100)
	
	totalLen = NetworkObj.Uint32("TotalLen", 100)
	commandId = NetworkObj.Uint32("CommandId", 0x11111002)
	sequenceId = NetworkObj.Uint32("sequenceId", 1)
	SccpPort = NetworkObj.Uint16("SccpPort", 4080)
	DccaPort = NetworkObj.Uint16("DccaPort", 4081)
	VacPort = NetworkObj.Uint16("VacPort", 4082)
	instance = NetworkObj.Char("instance", 2, '5')
	ipAddress = NetworkObj.Char("ipAddress", 20, '150.236.80.166')
	identity = NetworkObj.Char("identity", 60, 'isp.ericsson.com')

	index = 0
	index = totalLen.toStream(data, index) 
	print index 
	index = commandId.toStream(data, index) 
	print index 
	index = sequenceId.toStream(data, index) 
	print index 
	index = SccpPort.toStream(data, index) 
	print index 
	index = DccaPort.toStream(data, index) 
	print index 
	index = VacPort.toStream(data, index) 
	print index 
	index = instance.toStream(data, index) 
	print index 
	index = ipAddress.toStream(data, index) 
	print index 
	index = identity.toStream(data, index)
	print index 

	for i in range(10000):
		con.write(data)
	time.sleep(10)

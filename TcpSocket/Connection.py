#!/usr/local/bin/python
import threading
import socket
import time
import array

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
					if len(buf):
						self._logger.info(("len:" , len(buf))) 
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
	import NetworkObj

	con = Connection(logger.getLogger())
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
	
	con.write(data)
	time.sleep(10)

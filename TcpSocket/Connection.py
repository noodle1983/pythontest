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
	
	def __init__(self, logger, sock = None, addr = None, status = 'started', sniffer = None):
		self._status = status
		self._sock = sock		
		self._logger = logger
		self._addr = addr
		self._sniffer = sniffer
		self._wlock = threading.RLock()
		self._writeQueue = []
		self._readProcessor = Processor()
		self._writeProcessor = Processor(2)

		if self._sock:
			self._sock.settimeout(5)
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
		self._sock.settimeout(5)
		self.__startToHandleMsg()

	def stop(self):
		self._status = 'stopped'
		self._sock.close()
		
	def read(self):
		while self._status != 'stopped':
			try:
				buf = self._sock.recv(4096)
				if len(buf) == 0:
					self._logger.debug("[read]buf:%s" % (buf))
					raise socket.timeout
				self._logger.debug("[read]bufLen:%d\nbuffer:\n%s\n" % (len(buf), buf))
				#
				self.write(buf)
			except socket.error, e:
				if (str(e) == "timed out"):
					self._logger.debug("[read]time out!")
					if self._sniffer:
						return self._sniffer.registSock(self._sock, self.read, None, None)
					time.sleep(0.1)
				else:
					self._logger.debug("[read]socket.error!" + str(e))
					return self.shutdown()


		print "recv done"

	def write(self, buf):
		if self._status == 'stopped':
			return -1
		with self._wlock:
			self._writeQueue.append(buf)
		self._logger.debug("[write]queueLen:%d" % (len(self._writeQueue)))

	def writeList(self, list):
		if self._status == 'stopped':
			return -1
		with self._wlock:
			self._writeQueue += list
		self._logger.debug("[write]queueLen:%d" % (len(self._writeQueue)))

	def writeImpl(self):
		while self._status != 'stopped':
			if len(self._writeQueue) > 0: 
				buf = None
				with self._wlock: 
					buf = self._writeQueue.pop(0)
				self._logger.debug("[writeImpl]queueLen:%d" % (len(self._writeQueue)))
				self.__send(buf)	
			else:
				if self._sniffer:
					return self._sniffer.registSock(self._sock, None, self.writeImpl, None)
				time.sleep(0.1)	
				continue
		self._logger.debug("[writeImpl]quit send.")

	def __send(self, buf):
		try:
			self._sock.send(buf)
		except socket.error, e:
			if (str(e) == "timed out"):
				self._logger.debug("[write]time out, ignored!")
				if self._sniffer:
					return self._sniffer.registSoc14903k(self._sock, self.read, None, None)
				time.sleep(0.1)
			else:
				self._logger.warning("[__send]%s" % e)
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
	import Logger.logger as Logger
	import NetworkObj

	log = Logger.Logger()
	con = Connection(logger=log)
	con.connect('150.236.80.149', 9000)
	data = array.array('c', '0' * 12)
	
	totalLen = NetworkObj.Uint32("TotalLen", 12)
	commandId = NetworkObj.Uint32("CommandId", 0x10000003)
	sequenceId = NetworkObj.Uint32("sequenceId", 1)
	#SccpPort = NetworkObj.Uint16("SccpPort", 8080)
	#DccaPort = NetworkObj.Uint16("DccaPort", 8081)
	#VacPort = NetworkObj.Uint16("VacPort", 8082)
	#instance = NetworkObj.Char("instance", 2, '5')
	#ipAddress = NetworkObj.Char("ipAddress", 20, '150.236.80.227')
	#identity = NetworkObj.Char("identity", 60, 'isp.ericsson.com')

	index = 0
	index = totalLen.toStream(data, index) 
	print index 
	index = commandId.toStream(data, index) 
	print index 
	index = sequenceId.toStream(data, index) 
	print index 
#	index = SccpPort.toStream(data, index) 
#	print index 
#	index = DccaPort.toStream(data, index) 
#	print index 
#	index = VacPort.toStream(data, index) 
#	print index 
#	index = instance.toStream(data, index) 
#	print index 
#	index = ipAddress.toStream(data, index) 
#	print index 
#	index = identity.toStream(data, index)
#	print index 

	import time
	beginTime = time.time()
	msgCount = 100000
	queue = []
	for i in range(msgCount):
		#queue.append(data)
		con.write(data)
	#con.writeList(queue)

	while len(con._writeQueue):
	#while 1:
		time.sleep(0.1)
	con.shutdown()
	print "tps:%f"% (msgCount/(time.time() - beginTime))
	
	raw_input("input any key to quit.")

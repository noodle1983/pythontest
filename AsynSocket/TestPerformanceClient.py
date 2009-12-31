from ConnectionManager import ConnectionManager
from AsynClientSocket import AsynClientSocket
from SocketConnection import SocketConnection
from Processor import Processor
import SocketStatus
import CONST
import traceback
import time
import pdb

class Protocol:
	def __init__(self):
		self.msgCount = 1000
		self.msgLen = 128 
		self.datalen = self.msgCount * self.msgLen
		self.beginTime = 0
		self.recvCount = 0

	def addConnection(self, theConnection):
		self.connection = theConnection

	def handleInput(self, con): 
		"Protocol.handleInput"
		(buffer, len) = con.readRecvBuffer()
		#print "[Protocol.handleInput]buffer:", buffer
		self.recvCount += len
		#print "[Protocol.handleInput]", self.recvCount
		if self.recvCount >= self.datalen:
			self.endTime = time.time()
			print "time:%d, msgCount:%d, dataLen:%d, recvLen:%d, sendLen:%d, tps:%d" % \
				(self.endTime - self.beginTime, self.msgCount, self.datalen, self.recvCount, con.sendBuffer.totalRead, self.msgCount/(self.endTime - self.beginTime)) 
			con.close()

	def handleConnected(self, con):
		"Protocol.handleConnected"
		print "[Protocol.handleConnected]"
		self.beginTime = time.time()
		sendArray = [str(i)*self.msgLen for i in range(0, 10)]
		i = 0
		while i < self.msgCount:
			try:
				con.send(sendArray[i%10], self.msgLen)
				i += 1
			except:
				continue

		endTime = time.time() 
		print "time:%d, msgCount:%d, dataLen:%d, dataWrite:%d, tps:%d" % \
			(endTime - self.beginTime, self.msgCount, self.datalen, con.sendBuffer.totalWrite, self.msgCount/(endTime - self.beginTime)) 

	def handleError(self, con, str):
		"Protocol.handleError"
		print "[Protocol.handleError]" , str
		print con.dump()

	def handleClose(self, con):
		"Protocol.close"
		pass

processor = Processor(4)
manager = ConnectionManager()
host = "127.0.0.1"
port = 10000
testTimeout = 30

def testSend():
	print '=' * 60
	print '-' * 20, 'testSend', '-'* 20
	protocol = Protocol()
	newSock = AsynClientSocket()

	connection = SocketConnection(newSock, protocol, processor)
	manager.addConnection(newSock.getFileNo(), connection)
	assert len(manager) == 1

	connection.connect(host, port)

	timeout = 0
	while not connection.status.has(CONST.STATUS_UD) and timeout < testTimeout:
		time.sleep(1)
		timeout += 1
	
	if timeout >= testTimeout:
		pdb.set_trace()

	manager.clean()

	assert len(manager) == 0 
	print '-' * 20, 'test done', '-' * 20
	print '=' * 60


try:
	processor.start()
	manager.start()
	
	for i in range(0,1000):
		testSend()
except:
	print "-"*20 +  'Exception' + '-'* 20
	print traceback.print_exc()
	print "-"*20 + '---------' + '-'* 20
	print "test failed"
finally:
	processor.stop()
	manager.stop()

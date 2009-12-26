from ConnectionManager import ConnectionManager
from AsynClientSocket import AsynClientSocket
from SocketConnection import SocketConnection
from Processor import Processor
import SocketStatus
import CONST
import traceback
import time

class Protocol:
	def _init__(self):
		pass

	def addConnection(self, theConnection):
		self.connection = theConnection

	def handleInput(self): 
		"Protocol.handleInput"
		print "[Protocol.handleInput]", self.connection.recv()

	def handleConnected(self):
		"Protocol.handleConnected"
		pass

	def handleError(self, str):
		"Protocol.handleError"
		print "[Protocol.handleError]" , str

	def close(self):
		"Protocol.close"
		pass

processor = Processor(4)
manager = ConnectionManager()
host = "192.168.10.1"
port = 8008
def testConnectSuccess():
	print '=' * 60
	print '-' * 20, 'testConnectSuccess', '-'* 20
	protocol = Protocol()
	newSock = AsynClientSocket()

	connection = SocketConnection(newSock, protocol, processor)
	manager.addConnection(newSock.getFileNo(), connection)
	assert len(manager) == 1

	connection.connect(host, port)

	sleepTime = 5
	while not connection.status.has(CONST.STATUS_C) and sleepTime > 0:
		time.sleep(1)
		sleepTime = sleepTime - 1
	assert sleepTime > 0

	newSock.status.addStatus(CONST.STATUS_UD)
	manager.clean()

	assert len(manager) == 0 
	print '-' * 20, 'test done', '-' * 20
	print '=' * 60

def testConnectFailed():
	print '=' * 60
	print '-' * 20, 'testConnectFailed', '-'* 20
	protocol = Protocol()
	newSock = AsynClientSocket()

	connection = SocketConnection(newSock, protocol, processor)
	manager.addConnection(newSock.getFileNo(), connection)
	assert len(manager) == 1

	print "connect failed immediately."
	connection.connect("localhost", 12345)
	sleepTime = 5
	while not connection.status.has(CONST.STATUS_E) and sleepTime > 0:
		time.sleep(1)
		sleepTime = sleepTime - 1
	assert sleepTime > 0
	connection.status.dump()
	
	print "\n\nconnect failed later."
	connection.connect("202.38.193.244", 12345)
	sleepTime = 5
	while not connection.status.has(CONST.STATUS_E) and sleepTime > 0:
		time.sleep(1)
		sleepTime = sleepTime - 1
	assert sleepTime > 0
	connection.status.dump()

	newSock.status.addStatus(CONST.STATUS_UD)
	manager.clean()

	assert len(manager) == 0 
	print '-' * 20, 'test done', '-' * 20
	print '=' * 60

def testSend():
	print '=' * 60
	print '-' * 20, 'testSend', '-'* 20
	protocol = Protocol()
	newSock = AsynClientSocket()

	connection = SocketConnection(newSock, protocol, processor)
	manager.addConnection(newSock.getFileNo(), connection)
	assert len(manager) == 1

	connection.connect(host, port)
	while not connection.status.has(CONST.STATUS_C):
		time.sleep(1)

	for i in range(1, 5):
		connection.send(str(i)*i, i)
		while connection.recvBuffer.dataLen() <= 0:
			time.sleep(1)
		assert connection.recvBuffer.read() == (str(i)*i, i)

	newSock.status.addStatus(CONST.STATUS_UD)
	manager.clean()

	assert len(manager) == 0 
	print '-' * 20, 'test done', '-' * 20
	print '=' * 60


try:
	processor.start()
	manager.start()

	testConnectSuccess()
	testConnectFailed()
	testSend()
except:
	print "-"*20 +  'Exception' + '-'* 20
	print traceback.print_exc()
	print "-"*20 + '---------' + '-'* 20
	print "test failed"
finally:
	processor.stop()
	manager.stop()

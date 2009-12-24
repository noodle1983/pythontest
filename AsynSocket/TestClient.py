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

	def handleInput(self): 
		"Protocol.handleInput"
		pass

	def handleConnected(self):
		"Protocol.handleConnected"
		pass

	def handleError(self, str):
		"Protocol.handleError"
		print "[Protocol.handleError]" , str

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

	while not connection.status.has(CONST.STATUS_C):
		time.sleep(1)
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
	while not connection.status.has(CONST.STATUS_E):
		time.sleep(1)
	connection.status.dump()
	
	print "\n\nconnect failed later."
	connection.connect("202.38.193.244", 12345)
	while not connection.status.has(CONST.STATUS_E):
		time.sleep(1)
	connection.status.dump()

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
except:
	print "-"*20 +  'Exception' + '-'* 20
	print traceback.print_exc()
	print "-"*20 + '---------' + '-'* 20
	print "test failed"
finally:
	processor.stop()
	manager.stop()

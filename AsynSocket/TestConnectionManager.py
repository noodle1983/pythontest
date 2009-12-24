from ConnectionManager import ConnectionManager
from AsynClientSocket import AsynClientSocket
from SocketConnection import SocketConnection
import SocketStatus
import CONST
import traceback

class Processor:
	def __init__(self, thread):
		self.list = []

	def dump(self):
		dumpStr = "["
		for i in range(0, len(self.list)):
			dumpStr += "job %d:%s; "% (i, self.list[i].func_name)
		dumpStr += "]"
		return dumpStr	

	def process(self, fd, job):
		self.list.append(job)

	def processList(self,fd, theList):
		self.list += theList
		
class Protocol:
	def _init__(self):
		pass

	def handleInput(self): 
		"Protocol.handleInput"
		pass

	def handleConnected(self):
		"Protocol.handleConnected"
		pass

def testAddSocket():
	print '=' * 60
	print '-' * 20, 'testAddSocket', '-'* 20
	manager = ConnectionManager()
	processor = Processor(4)
	protocol = Protocol()
	newSock = AsynClientSocket()
	connection = SocketConnection(newSock, protocol, processor)
	manager.addConnection(newSock.getFileNo(), connection)
	assert len(manager) == 1

	newSock.status.addStatus(CONST.STATUS_UD)
	manager.clean()

	assert len(manager) == 0 
	print '-' * 20, 'test done', '-' * 20
	print '=' * 60

def testConnectedJob():
	print '=' * 60
	print '-' * 20, 'testConnectedJob', '-'* 20
	manager = ConnectionManager()
	processor = Processor(4)
	protocol = Protocol()
	newSock = AsynClientSocket()
	connection = SocketConnection(newSock, protocol, processor)
	
	manager.addConnection(newSock.getFileNo(), connection)

	assert len(manager) == 1 

	newSock.status.addStatus(CONST.STATUS_WF)

	connection.genJobs()

	assert connection.status.has(CONST.STATUS_C)
	assert processor.list[-1].__doc__ == "Protocol.handleConnected"

	print newSock.dump()
	print processor.dump()
	print '-' * 20, 'test done', '-' * 20
	print '=' * 60

def testSendJob():
	print '=' * 60
	print '-' * 20, 'testSendJob', '-'* 20
	manager = ConnectionManager()
	processor = Processor(4)
	protocol = Protocol()
	newSock = AsynClientSocket()
	connection = SocketConnection(newSock, protocol, processor)
	
	manager.addConnection(newSock.getFileNo(), connection)

	assert len(manager) == 1 

	newSock.status.addStatus(CONST.STATUS_WF)
	connection.genJobs()
	assert processor.list[-1].__doc__ == "Protocol.handleConnected"
	connection.send("test", 5)
	connection.genJobs()
	assert processor.list[-1].__doc__ == "AsynClientSocket.sendImpl"

	assert connection.status.has(CONST.STATUS_C)
	print newSock.dump()
	print processor.dump()
	print '-' * 20, 'test done', '-' * 20
	print '=' * 60

def testRecvJob():
	print '=' * 60
	print '-' * 20, 'testRecvJob', '-'* 19
	manager = ConnectionManager()
	processor = Processor(4)
	protocol = Protocol()
	newSock = AsynClientSocket()
	connection = SocketConnection(newSock, protocol, processor)
	
	manager.addConnection(newSock.getFileNo(), connection)

	assert len(manager) == 1 

	newSock.status.addStatus(CONST.STATUS_WF)
	connection.genJobs()
	print processor.list[-1].__doc__
	assert processor.list[-1].__doc__ == "Protocol.handleConnected"

	newSock.status.addStatus(CONST.STATUS_RF)
	connection.genJobs()
	print processor.list[-1].__doc__
	assert processor.list[-1].__doc__ == "SocketConnection.recvImpl"


	assert connection.status.has(CONST.STATUS_C)
	print newSock.dump()
	print processor.dump()
	print '-' * 20, 'test done', '-' * 20
	print '=' * 60

try:
	testAddSocket()
	testConnectedJob()
	testSendJob()
	testRecvJob()
except:
	print "-"*20 +  'Exception' + '-'* 20
	print traceback.print_exc()
	print "-"*20 + '---------' + '-'* 20
	print "test failed"

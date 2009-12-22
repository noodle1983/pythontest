from ConnectionManager import ConnectionManager
from AsynClientSocket import AsynClientSocket
from SocketConnection import SocketConnection
import SocketStatus
import CONST
import traceback

class Processor:
	def __init__(self):
		self.list = []

	def processList(self, theList):
		self.list += theList
		
class Protocol:
	def _init__(self):
		pass

	def handleInput(self): 
		pass

def testAddSocket():
	print '=' * 60
	print '-' * 20, 'testAddSocket', '-'* 20
	manager = ConnectionManager()

	processor = Processor()
	newSock = AsynClientSocket()
	connection = SocketConnection(
	manager.addSocket(newSock.getFileNo(), newSock)
	assert len(manager) == 1 

	newSock.status.addStatus(CONST.STATUS_UD)
	manager.clean()

	assert len(manager) == 0 
	print '-' * 20, 'test done', '-' * 20
	print '=' * 60

def testConnectedJob():
	print '=' * 60
	print '-' * 20, 'testConnectedJob', '-'* 20
	processor = Processor()
	manager = ConnectionManager(processor)

	newSock = AsynClientSocket()
	manager.addSocket(newSock.getFileNo(), newSock)
	assert len(manager) == 1 

	newSock.status.addStatus(CONST.STATUS_WF)
	print newSock.dump()

	manager.select()
	print '-' * 20, 'test done', '-' * 20
	print '=' * 60

try:
	testAddSocket()
	testConnectedJob()
except:
	print "-"*20 +  'Exception' + '-'* 20
	print traceback.print_exc()
	print "-"*20 + '---------' + '-'* 20
	print "test failed"

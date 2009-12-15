from SocketManager import SocketManager
from AsynClientSocket import AsynClientSocket
import SocketStatus
import CONST
import traceback

class Processor:
	def __init__(self):
		self.list = []

	def processList(self, theList):
		self.list += theList
		
def testAddSocket():
	print '=' * 60
	print '-' * 20, 'testAddSocket', '-'* 20
	processor = Processor()
	manager = SocketManager(processor)

	newSock = AsynClientSocket()
	manager.addSocket(newSock.getFileNo(), newSock)
	assert len(manager) == 1 

	newSock.status.addStatus(CONST.STATUS_UD)
	manager.clean()

	assert len(manager) == 0 
	print '-' * 20, 'test done', '-' * 20
	print '=' * 60

try:
	testAddSocket()
except:
	print "-"*20 +  'Exception' + '-'* 20
	print traceback.print_exc()
	print "-"*20 + '---------' + '-'* 20
	print "test failed"

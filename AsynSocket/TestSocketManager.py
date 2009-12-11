from SocketManager import SocketManager
from AsynClientSocket import AsynClientSocket

class Processor:
	def __init__(self):
		self.list = []

	def processList(self, theList):
		self.list += theList
		
def testAddSocket():
	processor = Processor()
	manager = SocketManager(processor)


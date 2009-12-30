from ConnectionManager import ConnectionManager
from AsynClientSocket import AsynClientSocket
from SocketConnection import SocketConnection
from Processor import Processor
from TcpServer import TcpServer
import SocketStatus
import CONST
import traceback
import time

class Protocol:
	def _init__(self):
		pass

	def addListenConnection(self, theConnection):
		self.connection = theConnection

	def handleInput(self, con): 
		"Protocol.handleInput"
		(buffer, len) = con.readRecvBuffer()
		if len > 0:
			#print "[Protocol.handleInput]buffer:", buffer
			con.send(buffer, len)

	def handleConnected(self, con):
		"Protocol.handleConnected"
		print "[Protocol.handleConnected]"
		msg = "Connected Echo Server. Your addr:%s\n" + str(con.addr)
		#con.send(msg, len(msg))

	def handleError(self, con, str):
		"Protocol.handleError"
		print "[Protocol.handleError]" ,con.addr,  str

	def handleClose(self, con):
		"Protocol.close"
		print "[Protocol.close]", con.addr

processor = Processor(4)
protocol = Protocol()
server = TcpServer(protocol, processor)
port = 10000
def testListen():
	print '=' * 60
	print '-' * 20, 'testListen', '-'* 20

	server.startAt(port)
	sleepTime = 3600 
	while sleepTime > 0:
		time.sleep(1)
		sleepTime = sleepTime - 1

	print '-' * 20, 'test done', '-' * 20
	print '=' * 60


try:
	processor.start()

	testListen()
except:
	print "-"*20 +  'Exception' + '-'* 20
	print traceback.print_exc()
	print "-"*20 + '---------' + '-'* 20
	print "test failed"
finally:
	processor.stop()
	server.close()

from ConnectionManager import ConnectionManager
from AsynClientSocket import AsynClientSocket
from SocketConnection import SocketConnection
from Processor import Processor
from TcpServer import TcpServer
import SocketStatus
import CONST
import traceback
import time
import socket
import errno

class Protocol:
	def _init__(self):
		pass

	def addListenConnection(self, theConnection):
		self.connection = theConnection

	def handleInput(self, con): 
		"Protocol.handleInput"
		(buffer, len) = con.readRecvBuffer()
		while len > 0:
			#print "[Protocol.handleInput]buffer:", buffer
			try:
				con.send(buffer, len)
				break
			except socket.error, e:
				if e.errno == errno.ENOBUFS:
					continue
				raise e

	def handleConnected(self, con):
		"Protocol.handleConnected"
		print "[Protocol.handleConnected]" + str(con.addr)
		msg = "Connected Echo Server. Your addr:%s\n" + str(con.addr)
		#con.send(msg, len(msg))

	def handleError(self, con, str):
		"Protocol.handleError"
		print "[Protocol.handleError]" ,con.addr,  str
		print "[Protocol.handleError]sendBuffer(r:%d, w:%d) recvBuffer(r:%d, w:%d)" %\
				(con.sendBuffer.totalRead, con.sendBuffer.totalWrite, \
				 con.recvBuffer.totalRead, con.recvBuffer.totalWrite)

	def handleClose(self, con):
		"Protocol.close"
		print "[Protocol.close]", con.addr
		if not con.errorWhenRecvNone:
			print "[Protocol.close]sendBuffer(r:%d, w:%d) recvBuffer(r:%d, w:%d)" %\
					(con.sendBuffer.totalRead, con.sendBuffer.totalWrite, \
					 con.recvBuffer.totalRead, con.recvBuffer.totalWrite)

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

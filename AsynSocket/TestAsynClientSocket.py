import select
from AsynClientSocket import *

import SocketStatus
import CONST

def testSendData():
	print '=' * 60
	print '-' * 20, 'testSendData', '-'* 20
	sock = AsynClientSocket()
	try:
		sock.connect('EV001F297A1A5C.eapac.ericsson.se', 8008)
	except socket.error, e:
		print e
		raw_input("test failed.")
		raise(e)

	print sock.dump()

	sockfds = []
	sockfds.append(sock.sock)
	
	wsockFds = sockfds
	sock.send("abcd", 4)
	while True:
		(infds, outfds, errfds) = select.select(sockfds, wsockFds, sockfds, 1)
		print "infds:", infds
		print "outfds:", outfds
		print "errfds:", errfds
		if infds:
			sock.status.addStatus(CONST.STATUS_RF)
		if outfds:
			sock.status.addStatus(CONST.STATUS_WF)
		if errfds:
			sock.status.addStatus(CONST.STATUS_E)
		print "after select:", sock.dump()

		sock.checkConnection()	
		print "after checkConnection:", sock.dump()
		
		if sock.status.get() & CONST.STATUS_WF:
			sock.sendImpl()
			wsockFds = []
			print "after send:", sock.dump()
		if sock.status.get() & CONST.STATUS_RF:
			sock.recvImpl()
			print "recv:", sock.recv()
			print "after recv:", sock.dump()
			break

	print '-' * 20, 'test done', '-' * 20
	print '=' * 60
testSendData()

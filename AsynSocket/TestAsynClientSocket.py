import select
from AsynClientSocket import *

def testSendData():
	print '=' * 60
	print '-' * 20, 'testSendData', '-'* 20
	sock = AsynClientSocket()
	try:
		sock.connect('EV001F297A1A5C.eapac.ericsson.se', 8008)
	except socket.error, e:
		print e
		raw_input("test failed.")

	print sock.dumpStatus()

	sockfds = []
	sockfds.append(sock.getFileNo())
	
	wsockFds = sockfds
	sock.send("abcd", 4)
	while True:
		(infds, outfds, errfds) = select.select(sockfds, wsockFds, sockfds, 1)
		print "infds:", infds
		print "outfds:", outfds
		print "errfds:", errfds
		if infds:
			sock.status.addStatus(STATUS_RF)
		if outfds:
			sock.status.addStatus(STATUS_WF)
		if errfds:
			sock.status.addStatus(STATUS_E)
		print "after select:", sock.dumpStatus()

		sock.checkConnection()	
		print "after checkConnection:", sock.dumpStatus()
		
		if sock.status.get() & STATUS_WF:
			sock.sendImpl()
			wsockFds = []
			print "after send:", sock.dumpStatus()
		if sock.status.get() & STATUS_RF:
			sock.recvImpl()
			print "recv:", sock.recv()
			print "after recv:", sock.dumpStatus()
			break

	print '-' * 20, 'test done', '-' * 20
	print '=' * 60
testSendData()

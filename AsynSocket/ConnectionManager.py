#/usr/local/bin/python
import threading
import time
import errno
import CONST
import SocketStatus
import select
import traceback

class ConnectionManager:

	def __init__(self):
		self.thread = threading.Thread(target=self.svc)
		self.running = False

		self.connections = {} 
		self.lock = threading.RLock()

		self.emptyLastTime = False

	def __len__(self):
		return len(self.connections)

	def addConnection(self, theFd, theConnection):
		orgConnection = self.connections.get(theFd)
		if orgConnection is None :
			with self.lock:
				self.connections[theFd] = theConnection
		elif orgConnection.status.has(CONST.STATUS_UD):
			with self.lock:
				self.connections[theFd] = theConnection
		else:
			orgConnection.reportError("[ConnectionManager.addConnection]file descriptor duplicated!")
			print orgConnection.sock.dump()
			theConnection.reportError("[ConnectionManager.addConnection]file descriptor duplicated!")

	def clean(self):
		with self.lock:
			newConnections = {}
			for (fd, con) in self.connections.items():
				if con.status.has(CONST.STATUS_UD):
					print "[ConnectionManager.clean]clean fd:%d, addr:%s"% (fd, con.addr)
					continue
				if fd != con.getFd():
					con.reportError("[ConnectionManager.clean]bad fd:%d, addr:%s"% (fd, con.addr))
					continue
				newConnections[fd] = con
			self.connections = newConnections
			print "[ConnectionManager.clean]fd after clean:%s" % self.connections.keys()

	def start(self):
		self.running = True
		self.thread.start()

	def stop(self):
		self.running = False
		self.thread.join()
		for con in self.connections.values():
			con.close()
		self.clean()

	def svc(self):
		while self.running:
			try:
				if self.emptyLastTime:
					time.sleep(0.001)

				if self.select():
					self.emptyLastTime = False
					self.genJobs()
				else:
					self.emptyLastTime = True
			except Exception, e:
				print "-"*20 +  'Exception' + '-'* 20
				print e
				print traceback.print_exc()
				print "-"*20 + '---------' + '-'* 20
				self.clean()
				continue

	def select(self):
		(rCandidate, wCandidate, eCandidate) = self.getSelectFds()
		if not rCandidate and not wCandidate and not eCandidate:
			return False
		#print "[ConnectionManager.select]Candidate:", rCandidate, wCandidate, eCandidate 
		(rReadys, wReadys, eReadys) = select.select(rCandidate, wCandidate, eCandidate, 0.001)

		#print "[ConnectionManager.select]Ready:", rReadys, wReadys, eReadys 
		for fd in rReadys:
			self.connections[fd].status.addStatus(CONST.STATUS_RF)
		for fd in wReadys:
			self.connections[fd].status.addStatus(CONST.STATUS_WF)
		for fd in eReadys:
			self.connections[fd].status.addStatus(CONST.STATUS_EF)
		return True

	def getSelectFds(self):
		"""
		return (readFds, writeFds, errFds)
		"""
		rCandidate = []
		wCandidate = []
		eCandidate = []
		with self.lock:
			for (fd, sock) in self.connections.items():
				if sock.status.get() == CONST.STATUS_N:
					rCandidate.append(fd)
					wCandidate.append(fd)
					eCandidate.append(fd)
					continue
				if (sock.status.get() & CONST.STATUS_SEL_READ_MASK) == CONST.STATUS_SEL_READ_CON :
					rCandidate.append(fd)
				if ((sock.status.get() & CONST.STATUS_SEL_WRITE_MASK) == CONST.STATUS_SEL_WRITE_CON )\
						and sock.hasDataToSend():
					wCandidate.append(fd)
				if not sock.status.has(CONST.STATUS_UD | CONST.STATUS_E | CONST.STATUS_EF):
					eCandidate.append(fd)
		return (rCandidate, wCandidate, eCandidate)

	def genJobs(self):
		rJobs = []
		wJobs = []
		with self.lock:
			for con in self.connections.values():
				con.genJobs()
				
	def dump(self):
		dumpStr = ""
		for con in self.connections.items():
			dumpStr += con.dump()


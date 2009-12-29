#/usr/local/bin/python
import threading
import time
import errno
import CONST
import SocketStatus
import select

class ConnectionManager:

	def __init__(self):
		self.thread = threading.Thread(target=self.svc)
		self.running = False

		self.connections = {} 
		self.lock = threading.RLock()

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
			theConnection.reportError("[ConnectionManager.addConnection]file descriptor duplicated!")

	def clean(self):
		with self.lock:
			self.connections = \
					dict([(k, v) for (k, v) in self.connections.items() if not v.status.has(CONST.STATUS_UD)])

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
				if self.select():
					self.genJobs()
				else:
					self.clean()
					time.sleep(0.001)
			except Exception, e:
				print e
				self.clean()
				continue

	def select(self):
		(rCandidate, wCandidate, eCandidate) = self.getSelectFds()
		if not rCandidate and not wCandidate and not eCandidate:
			return False
		#print "[ConnectionManager.select]Candidate:", rCandidate, wCandidate, eCandidate 
		(rReadys, wReadys, eReadys) = select.select(rCandidate, wCandidate, eCandidate, 1)

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
				if (sock.status.get() & CONST.STATUS_SEL_WRITE_MASK) == CONST.STATUS_SEL_WRITE_CON :
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
				

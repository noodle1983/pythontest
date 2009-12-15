#/usr/local/bin/python
import threading
import time
import errno
import CONST
import SocketStatus

class SocketManager:

	def __init__(self, theProcessor):
		self.processor = theProcessor

		self.thread = threading.Thread(target=self.run)
		self.running = False

		self.socketByFd = {} 
		self.lock = threading.RLock()

	def __len__(self):
		return len(self.socketByFd)

	def addSocket(self, theFd, theSocket):
		orgSocket = self.socketByFd.get(theFd)
		if orgSocket is None :
			with self.lock:
				self.socketByFd[theFd] = theSocket
		elif orgSocket.status.has(CONST.STATUS_UD):
			with self.lock:
				self.socketByFd[theFd] = theSocket
		else:
			raise socket.error(errno.EBADF, "SocketManager", "bad file descriptor")	

	def clean(self):
		with self.lock:
			self.socketByFd = \
					dict([(k, v) for (k, v) in self.socketByFd.items() if not v.status.has(CONST.STATUS_UD)])

	def start(self):
		self.running = True
		self.thread.start()

	def stop(self):
		self.running = False
		self.thread.join()
		for sock in self.socketByFd.values():
			sock.close()

	def run(self):
		while self.running:
			try:
				(rJobs, wJobs, eJobs) = self.select()
				if eJobs:
					self.processor.processList(eJobs)
				if rJobs:
					self.processor.processList(rJobs)
				if wJobs:
					self.processor.processList(wJobs)

			except Exception, e:
				print e
				self.clean()
				continue

	def select(self):
		(rCandidate, wCandidate, eCandidate) = self.getSelectFds()
		if not rCandidate and not wCandidate and not eCandidate:
			return ([], [], [])
		(rReadys, wReadys, eReadys) = select.select(rCandidate, wCandidate, eCandidate, 1)
		for fd in rReadys:
			self.socketByFd[fd].status.addStatus(CONST.STATUS_RF)
		for fd in wReadys:
			self.socketByFd[fd].status.addStatus(CONST.STATUS_WF)

		eJobs = []
		for fd in eReadys:
			ejobs.append(self.socketByFd[fd].reportError)

		(rJobs, wJobs) = self.genJobs()
		return (rJobs, wJobs, eJobs)

	def getSelectFds(self):
		"""
		return (readFds, writeFds, errFds)
		"""
		rCandidate = []
		wCandidate = []
		eCandidate = []
		with self.lock:
			for (fd, sock) in self.socketByFd.items():
				if (sock.status.get() & CONST.STATUS_SEL_READ_MASK) == CONST.STATUS_SEL_READ_CON :
					rCandidate.append(fd)
				if (sock.status.get() & CONST.STATUS_SEL_WRITE_MASK) == CONST.STATUS_SEL_WRITE_CON:
					wCandidate.append(fd)
				if not v.status.has(CONST.STATUS_UD | CONST.STATUS_E):
					eCandidate.append(fd)
		return (rCandidate, wCandidate, eCandidate)

	def genJobs(self):
		rJobs = []
		wJobs = []
		with self.lock:
			for (fd, sock) in self.socketByFd.items():
				if sock.status.has(CONST.STATUS_UD | CONST.STATUS_E): 
					continue
				if sock.status.has(CONST.STATUS_RF):
					rJobs.append(sock.recvImpl)
				if sock.status.has(CONST.STATUS_WF) and sock.status.has(CONST.STATUS_D):
					wJobs.append(sock.sendImpl)
		return (rJobs, wJobs)
				

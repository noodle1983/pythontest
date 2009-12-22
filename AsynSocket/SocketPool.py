#/usr/local/bin/python
import threading
import time
import errno
import CONST
import SocketStatus

class SocketPool:
	
	def __init__(self):
		self.socketByFd = {} 
		self.lock = threading.RLock()
	
	def append(self, fd, theSocket):
		orgSocket = self.socketByFd.get(fd)
		if orgSocket is None :
			with self.lock:
				self.socketByFd[fd] = theSocket
		elif orgSocket.status.has(CONST.STATUS_UD):
			with self.lock:
				self.socketByFd[fd] = theSocket
		else:
			raise socket.error(errno.EBADF, "SocketPool", "bad file descriptor")	

	def shutdown(self):
		for sock in self.socketByFd.values():
			sock.close()

	def clean(self):
		with self.lock:
			self.socketByFd = \
					dict([(k, v) for (k, v) in self.socketByFd.items() if not v.status.has(CONST.STATUS_UD)])

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
				if not v.status.has(CONST.STATUS_UD | CONST.STATUS_E)]:
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
				

					

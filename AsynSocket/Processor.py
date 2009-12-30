#/usr/local/bin/python
import threading
import time
import traceback

THREAD_STATUS_STOP = 0 
THREAD_STATUS_RUNNING = 1
THREAD_STATUS_IDLE = 2
THREAD_STATUS_ERROR = 4 

class Thread:
	"""
	combine thread with queue
	"""
	def __init__(self):
		self.status = THREAD_STATUS_STOP
		self.cond = threading.Condition()
		self.actionQueue = []
		self.threadImpl = threading.Thread(target=self.svc)

	def start(self):
		self.status = THREAD_STATUS_RUNNING
		self.threadImpl.start()

	def stop(self):
		self.status = THREAD_STATUS_STOP
		with self.cond:
			self.cond.notify()
		self.threadImpl.join()

	def processList(self, actionList):
		with self.cond:
			self.actionQueue += actionList
			self.cond.notify()

	def process(self, action):
		with self.cond:
			self.actionQueue.append(action)
			self.cond.notify()

	def svc(self):
		while self.status != THREAD_STATUS_STOP or len(self.actionQueue) > 0:
			with self.cond:
				while len(self.actionQueue) <= 0 and self.status != THREAD_STATUS_STOP:
					self.cond.wait()
				if len(self.actionQueue) <= 0:
					break
				action = self.actionQueue.pop(0)	
			try:
				action()	
			except:
				print traceback.print_exc()
				continue

				

class Processor:
	
	def __init__(self, threadCount = 1):
		self.threads = []
		self.nThread = threadCount
		for i in xrange(self.nThread):
			self.threads.append(Thread())

	def start(self):
		for thread in self.threads:
			thread.start()

	def stop(self):
		for thread in self.threads:
			thread.stop()

	def processList(self, id, actionList):
		tId = id % self.nThread
		self.threads[tId].processList(actionList)

	def process(self, id, action):
		tId = id % self.nThread
		self.threads[tId].process(action)

if __name__ == '__main__':
	def sayHello():
		print "hello"
	try:
		p = Processor(2)
		p.start()
		p.process(1, sayHello)
		p.processList(2, [sayHello, sayHello])
	finally:
		p.stop()

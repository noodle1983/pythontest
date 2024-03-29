#/usr/local/bin/python
import threading
import time
import sys
import os
sys.path.append(os.getcwd() + '/../')
sys.path.append(os.getcwd() + '/')

class Processor:
	
	def __init__(self, nThread = 1):
		self._status = ''
		self._threads = []
		self._lock = threading.RLock()
		self._actionQueue = []
		for i in xrange(nThread):
			self._threads.append(threading.Thread(target=self.svc))

	
	def start(self):
		self._status = 'start'
		for thread in self._threads:
			thread.start()
		self._status = 'started'

	def stop(self):
		self._status = 'stop'
		if self._status == 'started':
			for thread in self._threads:
				thread.join()
		self._status = 'stopped'

	def processList(self, actionList):
		with self._lock:
			self._actionQueue += actionList

	def process(self, action):
		with self._lock:
			self._actionQueue.append(action)

	def svc(self):
		while self._status != 'stop':
			with self._lock:
				if len(self._actionQueue) <= 0:
					time.sleep(1)
					continue
				action = self._actionQueue.pop(0)	
			action()	

if __name__ == '__main__':
	from Action import Action as Action
	p = Processor(2)
	p.start()
	p.process(Action().run)
	p.processList([Action().run, Action().run])
	p.stop()
	raw_input("put any key to exit.")	

import select

class Selector:

	def __init__(self, theSocketPool):
		self.socketPool = theSocketPool

	def select(self):
		(rCandidate, wCandidate, eCandidate) = self.socketPool.getSelectFds()
		(rReadys, wReadys, eReadys) = select.select(rCandidate, wCandidate, eCandidate, 1)
		for fd in rReadys:
			self.socketPool[fd].status.addStatus(CONST.STATUS_RF)
		for fd in wReadys:
			self.socketPool[fd].status.addStatus(CONST.STATUS_WF)
		for fd in eReadys:
			self.socketPool[fd].reportError("select error")

		(rJobs, wJobs) = self.socketPool.genJobs()

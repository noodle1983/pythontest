import threading
import array
import struct
class Buffer:

	def __init__(self, theSize = 1024 *1024):
		self.capability = theSize
		self.buffer = array.array('c', '0' * theSize)

		self.readb = 0
		self.reade = 0
		self.writeb = 0
		self.writee = theSize

		self.rlock = threading.RLock()
		self.wlock = threading.RLock()

		self.wraped = False

	def read(self, theBuffer):
		if self.readb == self.reade:
			return 0

		with self.rlock:
			len = self.reade - self.readb
			if len == 0:
				 return 0
			
			theBuffer = struct.unpack_from("%dc"%len, self.buffer, self.readb)[0]
			self.readb = self.readb + len


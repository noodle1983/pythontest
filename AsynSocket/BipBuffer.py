import threading
import socket
import errno
import array
import struct

class BipBuffer:
	"""
		support only 1 thread reading/writing
	"""

	def __init__(self, theCap):
		self.cap = theCap
		self.buff = array.array('c', '\0' * theCap) 

		self.rIndex = 0
		self.reIndex = 0
		self.wIndex = 0

		self.usingBufferB = False

	def write(self, theBuff, n):
		self.write_reserve(theBuff, n)
		self.write_confirm(n)

	def write_reserve(self, theBuff, n):
		if self.usingBufferB:
			self._writeBufferB(theBuff, n)	
		else:
			self._writeBufferA(theBuff, n)


	def write_confirm(self, n):
		self.wIndex = self.wIndex + n
		if not self.usingBufferB:
			self.reIndex = self.wIndex

	def _writeBufferA(self, theBuff, n):
		#enough space
		if n <= self.cap - self.wIndex:
			struct.pack_into("%ds"%n, self.buff, self.wIndex, theBuff)

		#not enough space
		else:
			self._makeBufferB()
			self._writeBufferB(theBuff, n)

	def _writeBufferB(self, theBuff, n):
		#enough space
		if n <= self.rIndex - self.wIndex:
			struct.pack_into("%ds"%n, self.buff, self.wIndex, theBuff)

		#not enough space
		else:
			raise socket.error(errno.ENOBUFS, "Buffer has not enough space to write", "BipBuffer._writeBufferB")	

	def _makeBufferB(self):
		self.wIndex = 0
		self.usingBufferB = True

	def _cancelBufferB(self):
		self.rIndex = 0
		self.reIndex = self.wIndex
		self.usingBufferB = False

	def readn(self, n):
		res = self.read_reserve(n)
		self.read_confirm(n)
		return res

	def read_reserve(self, n):
		if self.usingBufferB and self.rIndex == self.reIndex:
			self._cancelBufferB()
		if self.reIndex - self.rIndex <= 0:
			raise socket.error(errno.ENOBUFS, "Buffer has not enough data to read", "BipBuffer.read_reserve")
		else:
			return struct.unpack_from("%ds"%n, self.buff, self.rIndex)[0]	

	def read_confirm(self, n):
		self.rIndex = self.rIndex + n
		if self.usingBufferB and self.rIndex == self.reIndex:
			self._cancelBufferB()

	
	def read(self):
		n = self.reIndex - self.rIndex  
		if n > 0:
			return struct.unpack_from("%ds"%n, self.buff, self.rIndex)[0]	
		else:
			raise socket.error(errno.ENOBUFS, "Buffer has not enough data to read", "BipBuffer.read")

	def dump(self):
		print "----------------buffer---------------\n"\
				"buffer capability  :%d\n"\
				"buffer readIndex   :%d\n"\
				"buffer readendIndex:%d\n"\
				"buffer writeIndex  :%d\n"\
				"buffer usingBufferB:%d\n"\
				"buffer:\n%s\n"\
				%(self.cap, self.rIndex, self.reIndex, self.wIndex, self.usingBufferB, self.buff)

if __name__ == '__main__':
	def test_normal():
		buffer = BipBuffer(32)
		buffer.write('1', 1)
		if '1' != buffer.read():
			print "test_normal failed"
			buffer.dump()
			raise

	def test_wrap():
		buffer = BipBuffer(32)
		buffer.write('1234567890', 10)
		buffer.write('1234567890', 10)
		buffer.write('1234567890', 10)
		if '1234567890' != buffer.readn(10):
			print "test_wrap failed! data are not consistent!"
			buffer.dump()
			raise
		buffer.write('1234567890', 10)

		if True != buffer.usingBufferB:
			print "test_wrap failed! buffer should using BufferB"
			buffer.dump()
			raise
		for i in range(0, 3):
			if '1234567890' != buffer.readn(10):
				print "test_wrap failed! data are not consistent!"
				buffer.dump()
				raise
		if True == buffer.usingBufferB:
			print "test_wrap failed! buffer should using BufferB"
			buffer.dump()
			raise


	def test_performance():
		import time
		buffer = BipBuffer(32)
		bufferN = 10000
		countPerAction = 7
		def writeBuffer():
			i = 0
			while i < bufferN:
				ch = str(i%10)
				try:
					buffer.write(ch * (i%countPerAction + 1), (i%countPerAction + 1))
				except socket.error, e:
					if e.errno == errno.ENOBUFS:
						print "not enough buffer %d\n"% i
						#time.sleep(1)				
						continue
					else:
						print 'test failed, unknow error\n', e
						raise
				i = i + 1


		
		th = threading.Thread(target=writeBuffer)
		th.start()
		i = 0
		while i < bufferN:
			ch = str(i%10)
			try:
				if (ch * (i%countPerAction + 1)) != buffer.readn((i%countPerAction + 1)):
					print "test_wrap failed! data are not consistent!"
					buffer.dump()
					raise
			except socket.error, e:
				if e.errno == errno.ENOBUFS:
					print "no data to read %d\n"% i
					#time.sleep(1)				
					continue
				else:
					print 'test failed, unknow error\n', e
					raise
			i = i + 1
			
		th.join()
		buffer.dump()

	try:
		test_normal()
		test_wrap()
		test_performance()
		print "test ok"
	except Exception, e:
		print "test failed:"
		print e
	raw_input("")


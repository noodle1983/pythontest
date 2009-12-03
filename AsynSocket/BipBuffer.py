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
		res = self.readn_reserve(n)
		self.read_confirm(n)
		return res

	def readn_reserve(self, n):
		if self.usingBufferB and self.rIndex == self.reIndex:
			self._cancelBufferB()
		if self.reIndex - self.rIndex > 0:
			return struct.unpack_from("%ds"%n, self.buff, self.rIndex)[0]
		else:
			raise socket.error(errno.ENOBUFS, "Buffer has not enough data to read", "BipBuffer.readn_reserve")

	def read_confirm(self, n):
		self.rIndex = self.rIndex + n
		if self.usingBufferB and self.rIndex == self.reIndex:
			self._cancelBufferB()

	def read(self):
		(res, n) = self.read_reserve()
		self.read_confirm(n)
		return  (res, n)
		
	def read_reserve(self):
		if self.usingBufferB and self.rIndex == self.reIndex:
			self._cancelBufferB()
		n = self.reIndex - self.rIndex  
		if n > 0:
			return (struct.unpack_from("%ds"%n, self.buff, self.rIndex)[0], n)	
		else:
			raise socket.error(errno.ENOBUFS, "Buffer has not enough data to read", "BipBuffer.read")
		
	def dataLen(self):
		return self.reIndex - self.rIndex  

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
		print '-'*20, 'test_normal', '-'*20
		buffer = BipBuffer(32)
		buffer.write('1', 1)
		if '1' != buffer.readn(1):
			print "test_normal failed"
			buffer.dump()
			raise
		print "test ok"

	def test_wrap():
		print '-'*20, 'test_wrap', '-'*20
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
		print "test ok"


	def test_correct():
		print '-'*20, 'test_correct', '-'*20
		import time
		buffer = BipBuffer(32)
		bufferN = 1024
		countPerAction = 5 
		def writeBuffer():
			i = 0
			while i < bufferN:
				ch = str(i%10)
				try:
					buffer.write(ch * (i%countPerAction + 1), (i%countPerAction + 1))
				except socket.error, e:
					if e.errno == errno.ENOBUFS:
						#print "not enough buffer %d\n"% i
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
					#print "no data to read %d\n"% i
					#time.sleep(1)				
					continue
				else:
					print 'test failed, unknow error\n', e
					raise
			i = i + 1
			
		th.join()
		buffer.dump()
		print "test ok"

	def test_count():
		print '-'*20, 'test_count', '-'*20
		import time
		buffer = BipBuffer(32)
		bufferN = 1024 * 1024
		countPerAction = 5 
		def writeBuffer2():
			i = 0
			writeCount = 0
			while i < bufferN:
				ch = str(i%10)
				try:
					buffer.write(ch * countPerAction, countPerAction)
					writeCount = writeCount + countPerAction
				except socket.error, e:
					if e.errno == errno.ENOBUFS:
						#print "not enough buffer %d\n"% writeCount
						#buffer.dump()
						#time.sleep(1)				
						continue
					else:
						print 'test failed, unknow error\n', e
						raise
				i = i + 1
			print "write done. write times:%d, write count:%d" % (bufferN, writeCount)

		
		th = threading.Thread(target=writeBuffer2)
		th.start()
		readCount = 0 
		readTime = 0
		while readCount < bufferN*countPerAction:
			try:
				(data, n) = buffer.read()
				readCount = readCount + n 
				readTime = readTime + 1
				#print "read len:%d, read:%s" % (n, data)
			except socket.error, e :
				if e.errno == errno.ENOBUFS:
					#print "no data to read. readed:%d\n"% readCount
					#buffer.dump()
					#time.sleep(1)
					continue
				else:
					print 'test failed, unknow error\n', e
					raise
		th.join()
		print "read done. read times:%d, readCount:%d, average readed:%d" % (readTime, readCount, readCount/readTime)
		if buffer.dataLen() > 0:
			print "test_count error, remain buffer len:%d" % buffer.dataLen()
			buffer.dump()
			raise
		print "test ok"

	try:
		test_normal()
		test_wrap()
		#test_correct()
		test_count()
		print '-'*20, 'all_done', '-'*20
	except Exception, e:
		print "test failed:"
		print e
	raw_input("")


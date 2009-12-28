import threading
import socket
import errno
import array
import struct
import pdb

class BipBuffer:
	"""
		support only 1 thread reading/writing
	"""

	def __init__(self, theCap):
		self.cap = theCap
		self.buff = array.array('c', '\0' * theCap) 

		self.reset()

	def reset(self):
		self.rIndex = 0
		self.reIndex = 0
		self.wIndex = 0

		self.usingBufferB = False

		self.totalWrite = 0
		self.totalRead = 0
		self.switchLock = threading.RLock()
		self.bufferSwitch = 0

		self.rDebugInfo = {} 
		self.wDebugInfo = {} 

	def write(self, theBuff, wLen):
		self.write_reserve(theBuff, wLen)
		self.write_confirm(wLen)

	def write_reserve(self, theBuff, n):
		if self.usingBufferB:
			self._writeBufferB(theBuff, n)	
		else:
			self._writeBufferA(theBuff, n)


	def write_confirm(self, n):
		self.totalWrite = self.totalWrite + n

		if (self.totalWrite > self.totalRead + self.cap):
			pdb.set_trace()

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

	def _cancelBufferB(self, newRIndex = 0):
		self.rIndex = newRIndex 
		#bug report: reIndex = self.wIndex may be not newest.
		#write action with update it; if no write action, it make some buffer unread
		self.reIndex = self.wIndex 
		self.usingBufferB = False

	def readn(self, n):
		res = self.readn_reserve(n)
		self.read_confirm(n)
		return res

	def readn_reserve(self, rResrvLen):
		"""
		!!!check if need to cancelBufferB first
		"""
		if self.usingBufferB and self.rIndex == self.reIndex:
			self._cancelBufferB(0)
		if self.dataLen() >= rResrvLen:
			if self.reIndex - self.rIndex >= rResrvLen:
				return struct.unpack_from("%ds"%rResrvLen, self.buff, self.rIndex)[0]
			else:
				retBuffer = array.array('c', '\0' * rResrvLen) 
				lenSeg1 = self.reIndex - self.rIndex
				struct.pack_into("%ds"%lenSeg1, retBuffer, 0, struct.unpack_from("%ds"%lenSeg1, self.buff, self.rIndex)[0])
				struct.pack_into("%ds"%(rResrvLen - lenSeg1), retBuffer, lenSeg1, struct.unpack_from("%ds"%(rResrvLen-lenSeg1), self.buff, 0)[0])
				return retBuffer.tostring()
		else:
			raise socket.error(errno.ENOBUFS, "Buffer has not enough data to read", "BipBuffer.readn_reserve")

	def read_confirm(self, cnfmLen):
		"""
		!!!self.reIndex can be trusted only once, writeThread may change it.
		!!!must not cancelBufferB when wrapedIndex
		"""
		self.totalRead = self.totalRead + cnfmLen

		wrapedIndex = self.rIndex + cnfmLen - self.reIndex
		if wrapedIndex > 0:
			if self.usingBufferB:
				self._cancelBufferB(wrapedIndex)
			else:
				self.rIndex = self.rIndex + cnfmLen
				if wrapedIndex - cnfmLen > 0:
					buffer.dump()
					raise "[BipBuffer.read_confirm]impossible, please check!"
		else:
			self.rIndex = self.rIndex + cnfmLen

	def read(self):
		try:
			(res, readedLen) = self.read_reserve()
			if readedLen > 0:
				self.read_confirm(readedLen)
			return  (res, readedLen)
		except:
			return ('', 0)
		
	def read_reserve(self):
		"""
		!!!check if need to cancelBufferB first
		"""
		if self.usingBufferB and self.rIndex == self.reIndex:
			self._cancelBufferB(0)
		n = self.dataLen()
		if n > 0:
			return (self.readn_reserve(n), n)
		else:
			return ('', 0)	
		
	def dataLen(self):
		if self.usingBufferB:
			return self.reIndex - self.rIndex + self.wIndex 
		else:
			return self.reIndex - self.rIndex

	def dump(self):
		print "----------------buffer---------------\n"\
				"buffer capability  :%d\n"\
				"buffer readIndex   :%d\n"\
				"buffer readendIndex:%d\n"\
				"buffer writeIndex  :%d\n"\
				"buffer usingBufferB:%d\n"\
				"buffer totalWrite  :%d\n"\
				"buffer totalRead   :%d\n"\
				%(self.cap, self.rIndex, self.reIndex, self.wIndex, self.usingBufferB, self.totalWrite, self.totalRead)

		if self.cap <= 100:
			print "buffer cap         :%s\n" % str(self.buff)

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

		readed = buffer.readn(30)
		if '123456789012345678901234567890' != readed:
			print str(readed)
			print "test_wrap failed! data are not consistent!"
			buffer.dump()
			raise
		if True == buffer.usingBufferB:
			print "test_wrap failed! buffer should using BufferB"
			buffer.dump()
			raise
		print "test ok"


	def test_correct(theCountPerAction = 5):
		print '-'*20, 'test_correct(', theCountPerAction, ')', '-'*20
		import time
		buffer = BipBuffer(32)
		bufferN = 1024
		countPerAction = theCountPerAction%32 
		def writeBuffer():
			i = 0
			while i < bufferN:
				ch = str(i%10)
				try:
					buffer.wDebugInfo[i%20] = "[i:%d, wIndex:%d, rIndex:%d, reIndex:%d, ba:%d, data:%s]" % \
						(i, buffer.wIndex, buffer.rIndex, buffer.reIndex, buffer.usingBufferB, ch * (i%countPerAction + 1))
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
				buffer.rDebugInfo[i%20] = "[i:%d, wIndex:%d, rIndex:%d, reIndex:%d, ba:%d]" % (i, buffer.wIndex, buffer.rIndex, buffer.reIndex, buffer.usingBufferB)
				expected = ch * (i%countPerAction + 1)
				readed = buffer.readn((i%countPerAction + 1))
				if expected != readed:
					print "data are not consistent![i:%d][readed:%s][expected:%s]" % (i,readed, expected)
					buffer.dump()
					pdb.set_trace()
			except socket.error, e:
				if e.errno == errno.ENOBUFS:
					#print "no data to read %d\n"% i
					#time.sleep(1)				
					continue
				else:
					print 'test failed, unknow error\n', e
					raise
					return
			i = i + 1
			
		th.join()
		print "test ok"

	def test_count(theCountPerAction = 5):
		print '-'*20, 'test_count(', theCountPerAction, ')', '-'*20
		import time
		buffer = BipBuffer(32)
		bufferN = 1024 
		countPerAction = theCountPerAction%32 
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
				#finally:
				#	print "-->TotalWrite:%d, TotalRead:%d, ri:%d, re:%d, wi:%d, ba:%d, dl:%d" % (buffer.totalWrite, buffer.totalRead, buffer.rIndex, buffer.reIndex, buffer.wIndex, buffer.usingBufferB, buffer.dataLen())
				i = i + 1
			print "write done. write times:%d, write count:%d" % (bufferN, writeCount)

		
		th = threading.Thread(target=writeBuffer2)
		th.start()
		readCount = 0 
		readTime = 0
		hitTimes = 0
		totalTimes = 20000
		readTimeAfterWriteDone = 100
		readTimeWhenWriteDone = 0
		while readCount < bufferN*countPerAction:
		#while readCount < bufferN*countPerAction and totalTimes > 0:
			totalTimes = totalTimes - 1
			try:
				(data, n) = buffer.read()
				readCount = readCount + n 
				readTime = readTime + 1
				if n:
					hitTimes = hitTimes + 1
				#print "read len:%d, read:%s" % (n, data)
				if buffer.totalWrite == bufferN*countPerAction:
					if readTimeWhenWriteDone == 0:
						readTimeWhenWriteDone = readTime 
					elif readTimeWhenWriteDone + readTimeAfterWriteDone < readTime:
						print 'can not stop reading'
						pdb.set_trace()
			except socket.error, e :
				if e.errno == errno.ENOBUFS:
					print "no data to read. readed:%d\n"% readCount
					#buffer.dump()
					#time.sleep(1)
					continue
				else:
					print 'test failed, unknow error\n', e
					raise
			#finally:
			#	print "<--TotalWrite:%d, TotalRead:%d, ri:%d, re:%d, wi:%d, ba:%d, readed:%d" % (buffer.totalWrite, buffer.totalRead, buffer.rIndex, buffer.reIndex, buffer.wIndex, buffer.usingBufferB, n)

		th.join()
		print "read done. read times:%d, hit times:%d, readCount:%d, average readed:%d" % (readTime, hitTimes, readCount, readCount/hitTimes)
		if buffer.totalWrite != buffer.totalRead:
			print "test_count error, TotalWrite:%d, TotalRead:%d, diff:%d" % (buffer.totalWrite, buffer.totalRead, buffer.totalWrite - buffer.totalRead)
			buffer.dump()
			raise
		if buffer.dataLen() > 0 or buffer.totalWrite != buffer.totalRead:
			print "test_count error, remain buffer len:%d" % buffer.dataLen()
			buffer.dump()
			raise
		print "test ok"

	import traceback
	try:
		test_normal()
		test_wrap()
		for i in range(0, 100):
			test_correct(5 + i%10)
			test_count( 5 + i%10)
		print '-'*20, 'all_done', '-'*20
	except Exception, e:
		print "test failed:"
		print e
		print traceback.print_exc()


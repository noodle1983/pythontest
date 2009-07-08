import array
import struct

class VarChar(object):
	def __init__(self, name, maxLen, value = ''):
		self._name = name
		self._value = value
		self._len = len(value)
		self._maxLen = maxLen 
		self._packFrmt = "%ds" % (self._len)

	def setValue(self, value):
		self._value = value
		self._len = len(value)
		self._packFrmt = "%ds" % (self._len)

	def getValue(self, value):
		return self._value

	def fromStream(self, buf, index, realLen):
		if index + realLen > buf.itemsize * buf.buffer_info()[1]:
			return -1
		self._packFrmt = "%ds" % (realLen)
		self.setValue(struct.unpack_from(self._packFrmt, buf, index)[0])
		return index + realLen 

	def toStream(self, buf, index):
		self._packFrmt = "%ds" % (self._len)
		struct.pack_into(self._packFrmt, buf, index, self._value)
		return index + self._len

	def toString(self):
		return "%s: %s" % (self._name, self._value)

class FixLenObj(object):
	def __init__(self, name, value, packFrmt, printFrmt, len):
		self._name = name
		self._value = value
		self._len = len 
		self._packFrmt = packFrmt 
		self._printFrmt = "%s: %" + printFrmt

	def setValue(self, value):
		self._value = value

	def getValue(self, value):
		return self._value

	def fromStream(self, buf, index):
		if index + self._len > buf.itemsize * buf.buffer_info()[1]:
			return -1
		self._value = struct.unpack_from(self._packFrmt, buf, index)[0]
		return index + self._len

	def toStream(self, buf, index):
		struct.pack_into(self._packFrmt, buf, index, self._value)
		return index + self._len

	def toString(self):
		return self._printFrmt % (self._name, self._value)

class Char(FixLenObj):
	def __init__(self, name, len, value = ''):
		super(Char, self).__init__(name, value, "%ds" % (len), "s", len)

class Int16(FixLenObj):
	def __init__(self, name, value = 0):
		super(Int16, self).__init__(name, value, "!h", "d", 2)

		
class Int32(FixLenObj):
	def __init__(self, name, value = 0):
		super(Int32, self).__init__(name, value, "!l", "d", 4)
		
class Int64(FixLenObj):
	def __init__(self, name, value = 0):
		super(Int64, self).__init__(name, value, "!q", "d", 8)

class Uint16(FixLenObj):
	def __init__(self, name, value = 0):
		super(Uint16, self).__init__(name, value, "!H", "d", 2)
		
class Uint32(FixLenObj):
	def __init__(self, name, value = 0):
		super(Uint32, self).__init__(name, value, "!L", "u", 4)
		
class Uint64(FixLenObj):
	def __init__(self, name, value = 0):
		super(Uint64, self).__init__(name, value, "!Q", "u", 8)

if __name__ == '__main__':
	d = Int16('int' , 12)
	print "toString:" + d.toString()

	import array
	a = array.array('c', '0' * 32)
	struct.pack_into("!h", a, 0, 32)

	print "%d, %d" % (a.itemsize, d.fromStream(a, 0))
	print "toString:" + d.toString()

	struct.pack_into("10s", a, 0, '01234567')
	s = Char("char", 10)

	print "%d, %d" % (a.itemsize, s.fromStream(a, 0))
	print "toString:" + s.toString()

	struct.pack_into("10s", a, 0, '01234567')
	v = VarChar("varchar", 10)

	print "%d, %d" % (a.itemsize, v.fromStream(a, 0, 8))
	print "toString:" + v.toString()



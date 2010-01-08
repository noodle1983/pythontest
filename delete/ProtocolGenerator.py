

class VectorSymbol:

	def __init__(self, name):
		self.name = name.capitalize()
		self.subSymbol = []
	
	def pyDef(self):
		defStr = ""
		defStr += self.pyDeclare()
		defStr += self.pyInit()
		defStr += self.pyFromStream()
		defStr += self.pyToStream()
		defStr += self.pyToString()
		return defStr

	def pyDeclare(self):
		return "\n\nclass %s:" % self.name 

	def pyInit(self):
		defStr = "\n\n\tdef __init__(self):"
		for field in self.subSymbol:
			defStr += field.pyInInit()
		return defStr

	def pyInInit(self):
		return "\n\t\tself.%sM = %s()" % (self.name, self.name)

	def pyFromStream(self):
		defStr = "\n\n\tdef fromStream(self, buf, rIndex, end):"
		for field in self.subSymbol:
			defStr += field.pyInFromStream()
		defStr += "\n\t\treturn rIndex"
		return defStr

	def pyInFromStream(self):
		defStr = "\n\t\trIndex += self.%sM.fromStream(buf, rIndex, end)" \
				% (self.name)
		return defStr

	def pyToStream(self):
		defStr = "\n\n\tdef toStream(self, buf, wIndex, end):"
		for field in self.subSymbol:
			defStr += field.pyInToStream()
		defStr += "\n\t\treturn wIndex"
		return defStr

	def pyInToStream(self):
		defStr = "\n\t\twIndex += self.%sM.toStream(buf, wIndex, end)" \
				% (self.name)
		return defStr

	def pyToString(self):
		defStr = "\n\n\tdef toString(self, nTab = 0):"
		defStr += "\n\t\ttoStr = '\\t' * nTab"
		defStr += "\n\t\ttoStr += '%s:'" % self.name
		for field in self.subSymbol:
			defStr += field.pyInToString()
		defStr += "\n\t\treturn toStr"
		return defStr

	def pyInToString(self):
		defStr = "\n\t\ttoStr += self.%sM.toString(nTab+1)" \
				% (self.name)
		return defStr



class HashSymbol():

	def __init__(self, name):
		self.name = name.capitalize()
		self.symbolById = {}
	
	def pyDef(self):
		defStr = ""
		defStr += self.pyDeclare()
		defStr += self.pyInit()
		defStr += self.pyFromStream()
		defStr += self.pyToStream()
		defStr += self.pyToString()
		return defStr

	def pyDeclare(self):
		return "\n\nclass %s:" % self.name 

	def pyInit(self):
		defStr = "\n\n\tdef __init__(self):"
		defStr += "\n\t\tself.symbolById = {\\"
		for (id, symbol) in self.symbolById.items():
			defStr += "\n\t\t\t%s:%s\\" % (id, symbol)
		defStr += "\n\t\t\t}"
		return defStr

	def pyInInit(self):
		return "\n\t\tself.%sM = %s" % (self.name, self.name)

	def pyFromStream(self):
		return ""

	def pyInFromStream(self):
		return "\n\t\tself.%sM = %s" % (self.name)
		defStr += "\n\t\trIndex += self.%sM.fromStream(buf, rIndex, end)" \
				% (self.name)
		return defStr

	def pyToStream(self):
		defStr = "\n\n\tdef toStream(self, buf, wIndex, end):"
		for field in self.subSymbol:
			defStr += field.pyInToStream()
		defStr += "\n\t\treturn wIndex"
		return defStr

	def pyInToStream(self):
		defStr = "\n\t\twIndex += self.%sM.toStream(buf, wIndex, end)" \
				% (self.name)
		return defStr

	def pyToString(self):
		defStr = "\n\n\tdef toString(self, nTab = 0):"
		defStr += "\n\t\ttoStr = '\\t' * nTab"
		defStr += "\n\t\ttoStr += '%s:'" % self.name
		for field in self.subSymbol:
			defStr += field.pyInToString()
		defStr += "\n\t\treturn toStr"
		return defStr

	def pyInToString(self):
		defStr = "\n\t\ttoStr += self.%sM.toString(nTab+1)" \
				% (self.name)
		return defStr

class BasicSymbol():

	def __init__(self, name, type, len):
		self.name = name.capitalize()
		self.type = type
		self.len = len
	
	def pyDef(self):
		defStr = ""
		defStr += self.pyDeclare()
		defStr += self.pyInit()
		defStr += self.pyFromStream()
		defStr += self.pyToStream()
		defStr += self.pyToString()
		return defStr

	def pyDeclare(self):
		return "\nclass %s(%s):\n" % (self.name, self.type) 

	def pyInit(self):
		defStr = """
	def __init__(self):
		super(%s, self).__init__('%s')
	""" % (self.name, self.name)
		return defStr

	def pyInInit(self):
		return "\n\t\tself.%sM = %s()" % (self.name, self.name)

	def pyFromStream(self):
		return ""

	def pyInFromStream(self):
		defStr = ""
		defStr += "\n\t\trIndex += self.%sM.fromStream(buf, rIndex, end)" \
				% (self.name)
		return defStr

	def pyToStream(self):
		return "" 

	def pyInToStream(self):
		defStr = ""
		defStr += "\n\t\twIndex += self.%sM.toStream(buf, wIndex, end)" \
				% (self.name)
		return defStr

	def pyToString(self):
		return ""

	def pyInToString(self):
		defStr = ""
		defStr += "\n\t\ttoStr += self.%sM.toString(nTab+1)" \
				% (self.name)
		return defStr

if __name__ == "__main__":
	vs = VectorSymbol("Hello")
	bs1 = BasicSymbol("B1", "Uint32", "4")
	bs2 = BasicSymbol("B2", "Uint32", "4")
	vs.subSymbol += [bs1, bs2]
	print vs.pyDef()

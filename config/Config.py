from xml.dom import minidom
from xml.dom.minidom import Node
from Element import Element
import re

	

class Config(object):
	

	def __init__(self, name='', value=0, desc=''):
		self.name = name
		self.value = value
		self.desc = desc

		self.min = None
		self.max = None
		self.default = None
		self.ref = None

		self.enums = {}
		self.minlen = None 
		self.maxlen = None
		self.fixlen = None

	def __str__(self):
		return "%s: %d" % (self._name, self._value)

	def fromXml(self, configElement):
		for ch in configElement.childNodes:
			if ch.nodeType != Node.ELEMENT_NODE \
				or ch.firstChild == None:
				continue
			e = Element().fromXml(ch)				
			if e.name == 'name':
				self.name = e.value
			else if e.name == 'desc':
				self.desc = e.value
			else if e.name == 'valuedef':
				self.valuedef = ValueDef().fromXml(ch)
		return self

if __name__ == '__main__':
	root = minidom.parseString("""<config type="int" ctrl="seq">
	<name>total len</name>
	<desc>total len</desc>
	<valuedef/>
</config>""")

	element = root.firstChild
	i = Int()
	i.fromXml(element)
	print i

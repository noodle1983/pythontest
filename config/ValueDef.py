from xml.dom import minidom
from xml.dom.minidom import Node
from Element import Element
import re

	

class ValueDef(object):
	
	def __init__(self):
		self.ref = None
		self.default = None
		self.enum = None 
		self.range = None
		self.len = None

	def fromXml(self, v):
		for ch in v.childNodes:
			if ch.nodeType != Node.ELEMENT_NODE: 
				continue
			e = Element().fromXml(ch)				
			if e.name == 'ref':
				self.ref = e.value
			elif e.name == 'default':
				self.default = e.value
			elif e.name == 'enum':
				self.enum = Enum().fromXml(ch)
			elif e.name == 'range':
				self.range = e.attrs
			elif e.name == 'len':
				self.len = e.attrs

		return self

if __name__ == '__main__':
	root = minidom.parseString("""
          <valuedef>
            <default>0</default>
            <len fix="4"></len>
          </valuedef>
""")

	e = root.firstChild
	v = ValueDef().fromXml(e)
	print v.default 
	print v.len.get('fix')
	print v.enum

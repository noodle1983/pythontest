from xml.dom import minidom
from xml.dom.minidom import Node
from Element import Element
from Enum import Enum
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

	def toXml(self):
		parent = Element('valuedef').toXml()

		ch = Element('ref', self.ref).toXml()
		parent.appendChild(ch)
		ch = Element('default', self.default).toXml()
		parent.appendChild(ch)
		ch = self.enum.toXml()
		parent.appendChild(ch)
		ch = Element(name = 'range', attrs = self.range).toXml()
		parent.appendChild(ch)
		ch = Element(name = 'len', attrs = self.range).toXml()
		parent.appendChild(ch)

		return parent

if __name__ == '__main__':
	root = minidom.parseString("""
	<valuedef>
	<ref   >aaa</ref>
	<default   >de</default>
	<range min="0" max="1"></range>
	<len fix="1" min="2" max="3"/>
	<enum>
		<enumitem id="0x01" desc="msg1"/>
		<enumitem id="0x02" desc="msg2"/>
	</enum>
	</valuedef>
""")

	e = root.firstChild
	v = ValueDef().fromXml(e)
	print v.toXml().toprettyxml()

from xml.dom import minidom
from xml.dom.minidom import Node
from Element import Element
import re

	

class Enum(object):
	
	def __init__(self):
		self.idOf = {}
		self.descOf = {}

	def fromXml(self, v):
		for ch in v.childNodes:
			if ch.nodeType != Node.ELEMENT_NODE: 
				continue
			e = Element().fromXml(ch)				
			if e.name == 'enumitem' and len(e.attrs) == 2:
				self.idOf[e.attrs['desc']] = e.attrs['id']
				self.descOf[e.attrs['id']] = e.attrs['desc']
		return self

if __name__ == '__main__':
	root = minidom.parseString("""
<enum>
	<enumitem id="0x01" desc="msg1"/>
</enum>
	""")

	e = root.firstChild
	enum = Enum().fromXml(e)
	print enum.idOf 
	print enum.descOf

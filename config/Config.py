from xml.dom import minidom
from xml.dom.minidom import Node
from Element import Element
from ValueDef import ValueDef
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
			elif e.name == 'desc':
				self.desc = e.value
			elif e.name == 'valuedef':
				self.valuedef = ValueDef().fromXml(ch)
		return self

	def toXml(self):
		parent = Element('config').toXml()
		
		ch = Element('name', self.name).toXml()		
		parent.appendChild(ch)

		ch = Element('desc', self.desc).toXml()
		parent.appendChild(ch)

		ch = self.valuedef.toXml()
		parent.appendChild(ch)

		return parent

if __name__ == '__main__':
	root = minidom.parseString("""
<config type="enum" ctrl="switcher" count="one">
	<name>commandId</name>
	<desc>command id</desc>
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
</config>
""")

	element = root.firstChild
	i = Config().fromXml(element)
	print i.toXml().toxml()
	print i.toXml().toprettyxml()

from xml.dom import minidom
from xml.dom.minidom import Node
from Element import Element
from ValueDef import ValueDef
import re

	

class Config(object):
	

	def __init__(self, name='', value=None, desc='' , attrs = None):
		self.name = name
		self.value = value
		self.desc = desc
		self.subconfig = []
		self.attrs =  {'type':'string', 'ctrl':'normal', 'count':'one'}
		if attrs is not None:
			for (k, v) in attrs.items():
				self.attrs[k] = v 

		self.min = None
		self.max = None
		self.default = None
		self.ref = None

		self.enums = {}
		self.minlen = None 
		self.maxlen = None
		self.fixlen = None

	def __str__(self):
		return self.toXml().toxml()

	def fromXml(self, configElement):
		for (key, value) in configElement.attributes.items():
			self.attrs[key] = value
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
			elif e.name == 'config':
				self.subconfig.append(Config().fromXml(ch))
		return self

	def toXml(self):
		parent = Element('config').toXml()
	
		for (key, value) in self.attrs.items():
			parent.setAttribute(key, value)

		ch = Element('name', self.name).toXml()		
		parent.appendChild(ch)

		ch = Element('desc', self.desc).toXml()
		parent.appendChild(ch)

		ch = self.valuedef.toXml()
		parent.appendChild(ch)

		for subcfg in self.subconfig:
			ch = subcfg.toXml()
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

</config>
""")

	element = root.firstChild
	i = Config().fromXml(element)
	print i
	print i.toXml().toprettyxml()
	raw_input('put any key to quit.')

from xml.dom import minidom
from xml.dom.minidom import Node
from Config import Config
from Element import Element
import re

	

class Configuration(object):
	

	def __init__(self, namespace=''):
		self.namespace = namespace
		self.subconfig = [] 

	def __str__(self):
		return self.toXml().toxml()

	def fromXml(self, configuration):
		self.namespace = configuration.attributes.get('namespace', '')
		
		for ch in configuration.childNodes:
			if ch.nodeType != Node.ELEMENT_NODE \
				or ch.firstChild == None:
				continue
			e = Element().fromXml(ch)				
			if e.name == 'config':
				self.subconfig.append(Config().fromXml(ch))
		return self

	def toXml(self):
		parent = Element('configuration').toXml()

		parent.setAttribute('namespace', self.namespace)
		
		for subcfg in self.subconfig:
			ch = subcfg.toXml()
			parent.appendChild(ch)

		return parent

if __name__ == '__main__':
	root = minidom.parseString("""
<configuration>
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
</configuration>
""")

	element = root.firstChild
	i = Configuration().fromXml(element)
	print i
	print i.toXml().toprettyxml()
	raw_input('put any key to quit.')

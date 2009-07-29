from xml.dom import minidom
from xml.dom.minidom import Node
import re

	

class Element(object):
	
	mFirstTag = re.compile("^<.*?>")
	mLastTag = re.compile("<.*?>$") 

	def __init__(self):
		self.name = None
		self.value = None
		self.attrs = {}

	def __str__(self):
		return "%s: %s" % (self.name, self.value)

	def fromXml(self, e):
		self.name = e.tagName
		self.value =Element.mLastTag.sub('', Element.mFirstTag.sub('', e.toxml())) 
		for (key, value) in e.attributes.items():
			self.attrs[key] = value

if __name__ == '__main__':
	root = minidom.parseString("""<config type="int" ctrl="seq">
	<name>total len</name>
	<desc>total len</desc>
	<valuedef/>
</config>""")

	e = root.firstChild
	i = Element()
	i.fromXml(e)
	print i

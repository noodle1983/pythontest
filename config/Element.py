from xml.dom import minidom
from xml.dom.minidom import Node
import re

	

class Element(object):
	
	mFirstTag = re.compile("^<.*?>")
	mLastTag = re.compile("<.*?>$") 

	def __init__(self, name = None, value = None, attrs = {}):
		self.name = name
		self.value = value
		self.attrs = {}

	def __str__(self):
		return "%s: %s" % (self.name, self.value)

	def fromXml(self, e):
		self.name = e.tagName
		self.value =Element.mLastTag.sub('', Element.mFirstTag.sub('', e.toxml())) 
		for (key, value) in e.attributes.items():
			self.attrs[key] = value
		return self

	def toXml(self):
		e = minidom.Element(self.name)	
		for (key, value) in self.attrs.items():
			e.setAttribute(key, value)
		text = minidom.Text()
		text.data = self.value
		e.appendChild(text)
		return e

if __name__ == '__main__':
	root = minidom.parseString("""<config type="int" ctrl="seq">
	valuedef
</config>""")

	e = root.firstChild
	i = Element()
	i.fromXml(e)
	print i.toXml().toxml()

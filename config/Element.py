from xml.dom import minidom
from xml.dom.minidom import Node
import re

	

class Element(object):
	
	mFirstTag = re.compile("^<.*?>\s*")
	mLastTag = re.compile("\s*<.*?>$") 

	def __init__(self, name = None, value = None, attrs = None ):
		self.name = name
		self.value = value
		if attrs is None:
			self.attrs =  {}
		else:
			self.attrs = attrs 

	def __str__(self):
		return self.toXml().toxml()

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
		if self.value is not None:
			text = minidom.Text()
			text.data = self.value
			e.appendChild(text)
		return e

if __name__ == '__main__':
	root = minidom.parseString("""<config type="int" ctrl="seq">
	valuedef
</config>""")

	e = root.firstChild
	i = Element().fromXml(e)
	print i
	print i.toXml().toprettyxml()
	raw_input('put any key to quit.')

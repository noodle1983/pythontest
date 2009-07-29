from xml.dom import minidom
from xml.dom.minidom import Node
import re

	

class Config(object):
	
	mFirstTag = re.compile("^<.*?>")
	mLastTag = re.compile("<.*?>$") 

	def __init__(self, name='', value=0, desc=''):
		self._name = name
		self._value = value
		self._desc = desc

		self._min = None
		self._max = None
		self._default = None
		self._ref = None

		self._enums = None
		self._minlen = None 
		self._maxlen = None
		self._fixlen = None

	def __str__(self):
		return "%s: %d" % (self._name, self._value)

	def getElementValue(self, element):
		return Int.mLastTag.sub('', Int.mFirstTag.sub('', element.toxml()))

	def fromXml(self, configElement):
		for ch in configElement.childNodes:
			if ch.nodeType != Node.ELEMENT_NODE \
				or ch.firstChild == None:
				continue
			if ch.tagName == 'name': 
				self._name = self.getElementValue(ch)
			else ch.tagName == 'desc':
				self._desc = self.getElementValue(ch)
			else  ch
				
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

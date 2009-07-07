from xml.dom import minidom

class LoadMsgDef(dict):
	def __init__(self, msgDefPath):
		super(LoadMsgDef, self).__init__()
		msgDefSt = minidom.parse('../xmldoc/' + msgDefPath)
		
		msgNodes = msgDefSt.getElementsByTagName('Msg')
		fields = []
		for msgNode in msgNodes:
			fieldNodes = msgNode.getElementsByTagName('Field')
			for fieldNode in fieldNodes:
				field = {}
				field['name'] = fieldNode.getAttribute('name')
				field['const'] = fieldNode.getAttribute('const')
				fields.append(field)
			self[msgNode.getAttribute('name')] = fields	

if __name__ == "__main__":
	print LoadMsgDef('SccpMsg.xml')

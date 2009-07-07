from xml.dom import minidom

# name, {type, length, default}
class LoadFieldsDef(dict):
	def __init__(self, fieldDefPath):
		super(LoadFieldsDef,self).__init__()
		fieldsDefSt = minidom.parse('../xmldoc/' + fieldDefPath)
		fieldsDefNodes = fieldsDefSt.getElementsByTagName('Field')
		for fieldDefNode in fieldsDefNodes:
			field = {}
			field['type'] = fieldDefNode.getAttribute('type')
			field['length'] = fieldDefNode.getAttribute('length')
			field['default'] = fieldDefNode.getAttribute('default')
			if field['type'] in ('complex', 'tlv'):
				subFieldNodes = fieldDefNode.getElementsByTagName('SubField')			
				subFields = []
				for subFieldNode in subFieldNodes:
					subField = {}
					subField['name'] = subFieldNode.getAttribute('name')
					subField['const'] = subFieldNode.getAttribute('const')
					subFields.append(subField)
				field['subFields'] = subFields
			self[fieldDefNode.getAttribute('name')] = field

if __name__ == "__main__":
	print LoadFieldsDef('SccpField.xml')

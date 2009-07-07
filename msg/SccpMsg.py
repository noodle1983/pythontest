#!/usr/bin/python -Wall

import sys;
sys.path.append('../interface')

from Msg import Msg
from LoadFieldsDef import LoadFieldsDef
from LoadMsgDef import LoadMsgDef
from xml.dom import minidom
import struct as st
import array
import re

class SccpMsgCodec(Msg):
	commonFields = {}
	msgs = {} 
	IntPackChar = {'1':'b', '2':'h', '4':'l', '8':'q'}
	def __init__(self):
		super(SccpMsgCodec, self).__init__()

	def fromStream(self, buff, len, msg):
		for msgName in self.msgs:
			if -1 != self.parseMsg(buff, len, self.msgs[msgName], msg):
				return True 
		return False 

	def parseMsg(self, buff, len, fieldList, msg):
		offset = self.parseFields(buff, 0, len, fieldList, msg) 	
		if  -1 == offset:
			return -1
		return offset
	
	def parseTlvField(self, buff, offset, len, fieldList, msg):
		if len(fieldList) < 3:
			return 0
		

	def parseFields(self, buff, offset, len, fieldList, msg):
		for field in fieldList:
			fieldDef = self.commonFields[field['name']]
			offset = self.parseField(buff, len, offset, field, fieldDef, msg)
			if -1 == offset:
				print 'can not parse ' + field['name']
				return -1
			elif len <= offset:
				return offset

	def parseField(self, msgBuf, len, offset, field, fieldDef, msg):
		retOffset = -1	
		value = None
		frmt = ""
		if 'integer' == fieldDef['type']:
			frmt = '!' + self.IntPackChar[fieldDef['length']]
			value = st.unpack_from(frmt, msgBuf, offset)
			msg[field['name']] = value[0]
			retOffset =  offset + int(fieldDef['length'])

		elif fieldDef['type'] in ('unsigned', 'incLen', 'excLen'):
			frmt = '!' + self.IntPackChar[fieldDef['length']].upper()
			value = st.unpack_from(frmt, msgBuf, offset)
			msg[field['name']] = value[0]
			if fieldDef['type'] in ('incLen', 'excLen'):	
				msg['_tmpLen'] = value[0]
			retOffset =  offset + int(fieldDef['length'])
		
		elif 'string' == fieldDef['type']:
			frmt = str(fieldDef['length']) + 's'
			value = st.unpack_from(frmt, msgBuf, offset)
			msg[field['name']] = value[0]
			retOffset =  offset + int(fieldDef['length'])

		elif 'stringBuf' == fieldDef['type']:
			frmt = str(msg['_tmpLen']) + 's'
			value = st.unpack_from(frmt, msgBuf, offset)
			msg[field['name']] = value[0]
			retOffset =  offset + msg['_tmpLen']  
		
		elif 'complex' == fieldDef['type']:
			retOffset = self.parseFields(msgBuf, offset, len, fieldDef['subFields'], msg) 			

		elif 'tlv' == fieldDef['type']:
			retOffset = self.parseFields(msgBuf, offset, len, fieldDef['subFields'], msg) 
			if retOffset == -1:
				return offset

		if field['const'] and self.myInt(field['const']) != value[0]:
			print 'field of ' + field['name'] + ' expect: ' + str(self.myInt(field['const'])) + ' but real:' + str(value[0])
			return -1
		return retOffset

	def toStream(self, msg):
		msgBuf = array.array('c', '\0' * 50)
		msgTail = 0
		fieldList = self.msgs[msg['_name']]
		msgTail = self.packTo(msg, fieldList, msgBuf, msgTail)
		return msgBuf, msgTail

	def packTo(self, msg, fieldList, msgBuf, msgTail):
		lenField = None
		for field in fieldList:
			msgTail, retField = self.packField(msg, field, msgBuf, msgTail)
			if retField:
				lenField = retField
		if lenField:
			msgTail = self.packLenField(lenField, msgBuf, msgTail)
		return msgTail 

	def packField(self, msg, field, msgBuf, msgTail):
		fieldDef = self.commonFields[field['name']]

		if fieldDef['type'] in ('excLen', 'incLen'):
			field['index'] = msgTail
			return msgTail + int(fieldDef['length']), field

		if field['const']:
			msg[field['name']] = field['const']

		if 'string' == fieldDef['type']:
			if msg.get(field['name']):
				if len(msg[field['name']]) > fieldDef['length']:
					msg[field['name']] = msg[field['name']][:fieldDef['length']]
				frmt = str(len(msg[field['name']])) + 's'
				st.pack_into(frmt, msgBuf, msgTail, str(msg[field['name']]))
				return msgTail + int(fieldDef['length']), None
			else:
				frmt = str(len(fieldDef['default'])) + 's'
				st.pack_into(frmt, msgBuf, msgTail, str(fieldDef['default']))
				return msgTail + int(fieldDef['length']), None

		if 'stringBuf' == fieldDef['type']:
			if msg.get(field['name']):
				if len(msg[field['name']]) > fieldDef['length']:
					msg[field['name']] = msg[field['name']][:fieldDef['length']]
				frmt = str(len(msg[field['name']])) + 's'
				st.pack_into(frmt, msgBuf, msgTail, str(msg[field['name']]))
				return msgTail + len(msg[field['name']]), None
			else:
				frmt = str(len(fieldDef['default'])) + 's'
				st.pack_into(frmt, msgBuf, msgTail, str(fieldDef['default']))
				return msgTail + len(msg[field['name']]), None
		
		if 'integer' == fieldDef['type']:
			if msg.get(field['name']):
				frmt = '!' + self.IntPackChar[fieldDef['length']]
				st.pack_into(frmt, msgBuf, msgTail, self.myInt(msg[field['name']]))
				return msgTail + int(fieldDef['length']), None
			else:
				frmt = '!' + self.IntPackChar[fieldDef['length']]
				st.pack_into(frmt, msgBuf, msgTail, self.myInt(fieldDef['default']))
				return msgTail + int(fieldDef['length']), None

		if 'unsigned' == fieldDef['type']:
			if msg.get(field['name']):
				frmt = '!' + self.IntPackChar[fieldDef['length']].upper()
				st.pack_into(frmt, msgBuf, msgTail, self.myInt(msg[field['name']]))
				return msgTail + int(fieldDef['length']), None
			else:
				frmt = '!' + self.IntPackChar[fieldDef['length']].upper()
				st.pack_into(frmt, msgBuf, msgTail, self.myInt(fieldDef['default']))
				return msgTail + int(fieldDef['length']), None
		
		if 'complex' == fieldDef['type']:
			return self.packTo(msg, field['subFields'], msgBuf, msgTaill), None

		if 'tlv' == fieldDef['type'] and msg.get(field['name']):
			return self.packTo(msg, fieldDef['subFields'], msgBuf, msgTail), None

		return msgTail, None

	def myInt(self, s):
		if -1 != s.find('x') or -1 != s.find('X'):
			return int(s, 0) 
		return int(s)

	def packLenField(self, field, msgBuf, msgTail):
		fieldDef = self.commonFields[field['name']]
		if 'incLen' == fieldDef['type']:
			frmt = '!' + self.IntPackChar[fieldDef['length']].upper()
			st.pack_into(frmt, msgBuf, field['index'], msgTail - field['index'])

		if 'excLen' == fieldDef['type']:
			frmt = '!' + self.IntPackChar[fieldDef['length']].upper()
			st.pack_into(frmt, msgBuf, field['index'], msgTail - field['index'] - int(fieldDef['length']))

		return msgTail


if __name__ == "__main__":
	SccpMsgCodec.commonFields = LoadFieldsDef('SccpField.xml')
	SccpMsgCodec.msgs = LoadMsgDef('SccpMsg.xml') 
	print 'common fields:' , SccpMsgCodec.commonFields	
	print 'msgs:', SccpMsgCodec.msgs
	msgCodec = SccpMsgCodec()
	msg = {'_name' : 'loginReq', \
			'sequenceId' : '11', \
			'smsContent': 'haha',\
			'SmsContentValue': 'haha'}
	buf, len = msgCodec.toStream(msg)
	print buf
	print '-' * 20
	msgRecieve = {}
	msgCodec.fromStream(buf, len, msgRecieve)
	print msgRecieve




import CONST

CONST.STATUS_N =  0    #None
CONST.STATUS_C =  0x01 #Connected
CONST.STATUS_E =  0x02 #Error status
# = 0x04
CONST.STATUS_EF = 0x08 #Error Flag, socket has an error event.
CONST.STATUS_RF = 0x10 #Read Flag, socket has data to read
CONST.STATUS_WF = 0x20 #Write Flag, socket can be writen to
CONST.STATUS_D =  0x40 #has data to send
CONST.STATUS_UD = 0x80 #user delete

CONST.STATUS_DESC = ['Connected', 'Error', 'Unkow', 'HasErrorEvent', \
		'SocketHasDataToRead', 'SocketCanWrite', 'HasDataToSend', 'UserStop']

CONST.STATUS_CONNECTED_MASK = CONST.STATUS_WF | CONST.STATUS_RF | CONST.STATUS_E | CONST.STATUS_UD
CONST.STATUS_CONNECTED_CON = CONST.STATUS_WF
CONST.STATUS_SEL_WRITE_MASK = CONST.STATUS_D | CONST.STATUS_WF | CONST.STATUS_UD | CONST.STATUS_E
CONST.STATUS_SEL_WRITE_CON  = CONST.STATUS_D | CONST.STATUS_C
"""
send workflow: 
	related status: CONST.STATUS_D, CONST.STATUS_WF. initialized 0;
	logic thread: put data to sending buffer, set status CONST.STATUS_D = 1
	select therad: 
		select write if CONST.STATUS_D = 1 and CONST.STATUS_WF = 0
		set CONST.STATUS_WF = 1 if socket is ready to send
		new send job if CONST.STATUS_WF = 1 and CONST.STATUS_D = 1
	send job: send all and set CONST.STATUS_D = 0 and CONST.STATUS_WF = 0
"""
CONST.STATUS_SEL_READ_MASK = CONST.STATUS_RF | CONST.STATUS_UD
CONST.STATUS_SEL_READ_CON = CONST.STATUS_N
"""
receive workflow:
	related status: CONST.STATUS_RF. initialized 0;
	select thread:
		select read if CONST.STATUS_RF = 0 
		set CONST.STATUS_RF = 1 if socket has data to read
		new read job if CONST.STATUS_RF = 1
	read job: read all and set CONST.STATUS_RF = 0
"""

"""
event notification:
        select write:
            send workflow: if CONST.STATUS_D = 1 and CONST.STATUS_WF = 0
            connect workflow: CONST.STATUS_C = 1
            receive workflow: ignore
            error workflow: CONST.STATUS_E = 0
        select read:
            send workflow: ignore
            connect workflow: ignore
            receive workflow: if CONST.STATUS_RF = 0 
            error workflow: CONST.STATUS_E = 0


"""

import threading
class SocketStatus:
	def __init__(self, theStatus = CONST.STATUS_N):
		self.lock = threading.RLock()
		self.status = theStatus

	def addStatus(self, theStatus):
		with self.lock:
			self.status = self.status | theStatus

	def rmStatus(self, theStatus):
		with self.lock:
			self.status = self.status & ~theStatus

	def set(self, theStatus = CONST.STATUS_N):
		with self.lock:
			self.status = theStatus

	def get(self):
		return self.status
	
	def has(self, theStatus):
		return self.status & theStatus

	def dump(self):
		strStatus = ["STATUS:"] 
		for i in range(0, len(CONST.STATUS_DESC)):
			if self.status & (1 << i):
				strStatus.append(CONST.STATUS_DESC[i]) 
		return strStatus


from logging import Handler
from logging.handlers import RotatingFileHandler
from datetime import datetime
from threading import RLock
import re

class TimedNameFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0,
                 encoding=None):
		self._index = 0;
		self._lock = RLock()
		self._p = re.compile("(_\d*){0,1}(_\d*){0,1}(\.\w*){0,1}$", re.IGNORECASE)
		RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding)
        
    def _open(self):
		with self._lock:
			self.baseFilename = self._p.sub('_' + datetime.now().strftime("%Y%m%d%H%M%S") + "_%03d"%(self._index) +  '.log', self.baseFilename) 
			self._index = (self._index + 1) % 1000 
		return RotatingFileHandler._open(self)
   		 
    
    def doRollover(self):
		self.stream.close()
		self.stream = TimedNameFileHandler._open(self)

import logging.handlers
logging.handlers.TimedNameFileHandler = TimedNameFileHandler

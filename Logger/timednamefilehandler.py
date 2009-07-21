from logging import Handler
from logging.handlers import RotatingFileHandler
from datetime import datetime
import re

class TimedNameFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0,
                 encoding=None):
		self._p = re.compile("(_\d*){0,1}(\.\w*){0,1}$", re.IGNORECASE)
		RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding)
        
    def _open(self):
		self.baseFilename = self._p.sub('_' + datetime.now().strftime("%Y%m%d%H%M%S") + '.log', self.baseFilename) 
		return RotatingFileHandler._open(self)
   		 
    
    def doRollover(self):
		self.mode = 'w'
		self.stream = self._open()

import logging.handlers
logging.handlers.TimedNameFileHandler = TimedNameFileHandler

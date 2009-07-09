import sys
import os
sys.path.append(os.getcwd() + '/../')
sys.path.append(os.getcwd() + '/')
from Logger.logger import Logger 

class Action(object):
	def __init__(self):
		pass

	def run(self):
		Logger().debug("default run")	
		pass

	def toString(self):
		return "default action"

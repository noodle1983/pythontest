# logger.py
import logging
import logging.config
from os import path

logger = None

def getLogger():
	configFilePath = path.dirname (path.realpath(__file__)) + '/logging.conf'
	logging.config.fileConfig(configFilePath)
	global logger
	logger = logging.getLogger("example")
	return logger

def debug(str):
	getLogger().debug(str)

def info(str):
	getLogger().info(str)

def warn(str):
	getLogger().warn(str)

def error(str):
	getLogger().error(str)

def critical(str):
	getLogger().critical(str)

if __name__ == '__main__':
	logger = getLogger()
	logger.debug("debug message")
	logger.info("info message")
	logger.warn("warn message")
	logger.error("error message")
	logger.critical("critical message")



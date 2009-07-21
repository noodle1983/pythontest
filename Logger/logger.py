# logger.py
import logging
import logging.config
from os import path
import timednamefilehandler

logger = None
consoleLogger = None

def ConsoleLogger():
	configFilePath = path.dirname (path.realpath(__file__)) + '/logging.conf'
	logging.config.fileConfig(configFilePath)
	global consoleLogger 
	consoleLogger = logging.getLogger("console")
	return consoleLogger

def Logger():
	configFilePath = path.dirname (path.realpath(__file__)) + '/logging.conf'
	logging.config.fileConfig(configFilePath)
	global logger
	logger = logging.getLogger("example")
	return logger

if __name__ == '__main__':
	logger = Logger()
	logger.debug("debug message")
	logger.info("info message")
	logger.warn("warn message")
	logger.error("error message")
	logger.critical("critical message")

	logger = ConsoleLogger()
	logger.debug("debug message")
	logger.info("info message")
	logger.warn("warn message")
	logger.error("error message")
	logger.critical("critical message")

	raw_input("input any key to quit.")

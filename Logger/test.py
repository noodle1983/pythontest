import logging

log = None
FORMAT = "[%(asctime)-15s %(levelname)-8s %(filename)s %(lineno)d] %(message)s"

def get_logger(format=FORMAT, datafmt=None):
	global log
	handler = logging.StreamHandler()
	fmt = logging.Formatter(format, datafmt)
	handler.setFormatter(fmt)
	
	log = logging.getLogger('uliweb')
	log.addHandler(handler)
	log.setLevel(logging.INFO)
	return log
	
if __name__ == '__main__':
	log = get_logger()
	log.error('This is an error %s', 'aaaa')
	log.warning('This is an warning')
	try:
		2/0
	except Exception, e:
		log.exception(e)


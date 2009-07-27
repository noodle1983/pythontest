
class Int:

	def __init__(self, name='IntName', value=0, desc='Intdesc'):
		self._name = name
		self._value = value
		self._desc = desc

		self._fixlen = None
		self._min = None
		self._max = None
		self._default = None

		self._ref = None
		self._enums = None
		self._minlen = None 
		self._maxlen = None


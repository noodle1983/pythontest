
class Bind1:
	def __init__(self, function, param1):
		self.function = function
		self.func_name = function.func_name
		self.param1 = param1
		self.__call__ = self.execute

	def execute(self):
		self.function(self.param1)

if __name__ == '__main__':
	def say(sth): print sth

	bind1 = Bind1(say, "Hello")
	bind1()

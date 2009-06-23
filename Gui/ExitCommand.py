
class ExitCommand:
	def __init__(self):
		pass

	def svc(self, event):
		print "exit now"
		raise SystemExit()	

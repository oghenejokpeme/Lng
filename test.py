class execl(object):
	def __init__(self):
		self.env = {}

	def eval(self):

		class insideClass(object):
			def __init__(self):
				self.test = []
				
		print "Mode!"
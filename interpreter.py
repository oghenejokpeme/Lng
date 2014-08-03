class W_Root(object):
	pass

class W_IntObject(W_Root):
	def __init__(self, intval):
		assert(isinstance(intval, int))
		self.intval = intval

	def r_self(self):
		return W_IntObject(self.intval)

	def std_out(self):
		return str(self.intval)

class W_ListObject(W_Root):
	def __init__(self, f_list):
		assert(isinstance(f_list, list))
		self.f_list = f_list

	def append(self, other):
		self.f_list.append(other)
		
	def r_self(self):
		return W_ListObject(self.f_list)

	def std_out(self):
		return str(self.f_list)

class W_BinOp(W_Root): 
	def __init__(self, lval, rval, op):
		self.lval = lval
		self.rval = rval
		self.op = op 

	def gen_ans(self):
		if self.op == '+':	
			return W_IntObject(self.lval.intval + self.rval.intval)
		if self.op == '-':	
			return W_IntObject(self.lval.intval - self.rval.intval)
		if self.op == '*':	
			return W_IntObject(self.lval.intval * self.rval.intval)
		if self.op == '/':	
			return W_IntObject(self.lval.intval / self.rval.intval)

class W_StrObject(W_Root):
	def __init__(self, strval):
		assert(isinstance(strval, str))
		self.strval = strval

	def lookup(self, ctx):
		try:
			return ctx.env[self.strval]
		except KeyError:
			pass

	def r_self(self):
		return W_StrObject(self.strval)

	def std_out(self):
		return str(self.strval)

class W_BoolObject(W_Root):
	def __init__(self, lvalue, cmp_op, rvalue):
		self.lvalue = lvalue
		self.cmp_op = cmp_op
		self.rvalue = rvalue

	def return_val(self):
		if self.cmp_op == '>':
			if self.lvalue > self.rvalue:
				return W_StrObject('True')
			else:
				return W_StrObject('False')	
		elif self.cmp_op == '>=':
			if self.lvalue >= self.rvalue:
				return W_StrObject('True')
			else:
				return W_StrObject('False')	
		elif self.cmp_op == '<':
			if self.lvalue < self.rvalue:
				return W_StrObject('True')
			else:
				return W_StrObject('False')	
		elif self.cmp_op == '<=':
			if self.lvalue <= self.rvalue:
				return W_StrObject('True')
			else:
				return W_StrObject('False')	
		elif self.cmp_op == '!=':
			if self.lvalue != self.rvalue:
				return W_StrObject('True')
			else:
				return W_StrObject('False')	
		elif self.cmp_op == '<>':
			if self.lvalue == self.rvalue:
				return W_StrObject('True')
			else:
				return W_StrObject('False')	


class Interpreter(W_Root):
	def __init__(self):
		self.env = {} #Global environment
		self.local_env = {} #Local environment for functions
		self.func_list = [] #List of all defined functions
		

		self.class_list = {} #List of all defined classes
		self.class_objects = {} #Mapping of object name to class name
		

#Function scoping hack.
class local_scope(W_Root):
	def __init__(self):
		self.env = {}

class class_scope(W_Root):
	def __init__(self):
		self.env = {}
		self.func_list = []
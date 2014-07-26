from rply.token import BaseBox
from rpython.rlib.jit import JitDriver 

class Node(BaseBox):
	def __eq__(self, other):
		if not isinstance(other, Node):
			return NotImplemented
		return (type(self) is type(other) and 
			self.__dict__ == other.__dict__)

	def __ne__(self, other):
		return not (self == other)

class Block(Node):
	def __init__(self, statements):
		self.statements = statements

	def getastlist(self):
		self.statementlist = []
		for statements in self.statements:
			self.statementlist.append(statements)

		return self.statementlist

	def eval(self, ctx):
		statements =  self.statements
		for returns in statements:
			#print returns
			returns.eval(ctx)

class Number(Node):
	def __init__(self, value):
		self.value = value

	def eval(self, ctx):
		from interpreter import W_FloatObject
		return W_FloatObject(self.value)
		
class Id(Node):
	def __init__(self, value):
		self.value = value

	def eval(self, ctx):
		from interpreter import W_StrObject
		return W_StrObject(self.value)

class String(Node):
	def __init__(self, expression):
		self.expression = expression
	
	def eval(self, ctx):
		if '\"' in self.expression:
			from interpreter import W_StrObject
			return W_StrObject(self.expression.strip('\"'))

class Assignment(Node):
	def __init__(self, lvalue, expression):
		self.lvalue = lvalue
		self.expression =  expression

	def eval(self, ctx):
		#print self.expression
		if isinstance(self.expression, Id):
			try: 
				reverse_ident = ctx.env[self.expression.eval(ctx).strval]
				ctx.env[self.lvalue.eval(ctx).strval] = reverse_ident
			except KeyError as e:
				raise Exception('Undefined assignment!')
				pass

		elif isinstance(self.expression, Number):
			ctx.env[self.lvalue.eval(ctx).strval] = self.expression.eval(ctx).r_self()

		elif isinstance(self.expression, String):
			ctx.env[self.lvalue.eval(ctx).strval] = self.expression.eval(ctx).r_self()			

		elif isinstance(self.expression, Binary_Operation) == True:
			ctx.env[self.lvalue.eval(ctx).strval] = self.expression.eval(ctx).r_self()
		#The following two conditions handle lists
		elif isinstance(self.expression, Block):
			values = []
			for list_val in self.expression.getastlist():
				values.append(list_val.eval(ctx))

			from interpreter import W_ListObject
			ctx.env[self.lvalue.eval(ctx).strval] = W_ListObject(values)

		elif isinstance(self.expression, List):
			values = []
			from interpreter import W_ListObject
			ctx.env[self.lvalue.eval(ctx).strval] = W_ListObject(values)

class Print(Node):
	def __init__(self, expression):
		self.expression = expression

	def eval(self, ctx):
		#print self.expression
		if isinstance(self.expression, String):
			print self.expression.eval(ctx).strval

		elif isinstance(self.expression, Id):
			try:
				output = ctx.env[self.expression.eval(ctx).strval]

				from interpreter import W_FloatObject, W_StrObject, W_ListObject

				if isinstance(output, W_FloatObject) or isinstance(output, W_StrObject):
					print output.std_out()
				elif isinstance(output, W_ListObject):
					list_values = []
					for value in output.f_list:
						list_values.append(value.floatval) #Change floatval to std_out() for a broad range of support

					print list_values

			except KeyError as e:
				print 'Undefined Variable:', e

		elif isinstance(self.expression, Binary_Operation):
			print self.expression.eval(ctx).std_out()

		elif isinstance(self.expression, Condition):
			print self.expression.eval(ctx).std_out()

class Condition(Node): #Condition should return string that says True or False
	def __init__(self, lvalue, cmp_op, rvalue):
		self.lvalue = lvalue
		self.cmp_op = cmp_op
		self.rvalue = rvalue
	
	def eval(self, ctx):
		from interpreter import W_BoolObject, W_FloatObject, W_StrObject
		#print self.lvalue.eval(ctx), self.rvalue.eval(ctx)
		if isinstance(self.lvalue.eval(ctx), W_FloatObject) and isinstance(self.rvalue.eval(ctx), W_FloatObject):
			return W_BoolObject(self.lvalue.eval(ctx).floatval, self.cmp_op, self.rvalue.eval(ctx).floatval).return_val()

		elif isinstance(self.lvalue.eval(ctx), W_StrObject) and isinstance(self.rvalue.eval(ctx), W_StrObject):
			return W_BoolObject(self.lvalue.eval(ctx).lookup(ctx).floatval, self.cmp_op, self.rvalue.eval(ctx).lookup(ctx).floatval).return_val()

		elif isinstance(self.lvalue.eval(ctx), W_StrObject) and isinstance(self.rvalue.eval(ctx), W_FloatObject):
			return W_BoolObject(self.lvalue.eval(ctx).lookup(ctx).floatval, self.cmp_op, self.rvalue.eval(ctx).floatval).return_val()
		
		elif isinstance(self.lvalue.eval(ctx), W_FloatObject) and isinstance(self.rvalue.eval(ctx), W_StrObject):
			return W_BoolObject(self.lvalue.eval(ctx).floatval, self.cmp_op, self.rvalue.eval(ctx).lookup(ctx).floatval).return_val()

class If(Node):
	def __init__(self, condition, ifstatements, elsestatements):
		self.condition = condition
		self.ifstatements = ifstatements
		self.elsestatements = elsestatements

	def eval(self, ctx):
		if self.elsestatements is None:
			if self.condition.eval(ctx).std_out() == 'True': #self.condition here is an object of the W_StrObject class
				intern_states = self.ifstatements.getastlist()
				for nodes in intern_states:
					nodes.eval(ctx)
			elif self.condition.eval(ctx).std_out() == 'False':
				pass
		elif isinstance(self.elsestatements, Block):
			if self.condition.eval(ctx).std_out() == 'True': #self.condition here is an object of the W_StrObject class
				for nodes in self.ifstatements.getastlist():
					nodes.eval(ctx)
			elif self.condition.eval(ctx).std_out() == 'False':
				for nodes in self.elsestatements.getastlist():
					nodes.eval(ctx)

jitdriver = JitDriver(greens=['condition'], reds=[])

class While(Node):
	def __init__(self, condition, statements):
		self.condition = condition
		self.statements = statements

	def eval(self, ctx):
		condition = self.condition.eval(ctx).std_out()

		while True:
			jitdriver.jit_merge_point(condition=condition)
			condition = self.condition.eval(ctx).std_out()

			if not condition is 'True':
				break

			self.statements.eval(ctx)
		'''
		while condition is 'True':
			jitdriver.jit_merge_point(condition=condition)

			self.statements.eval(ctx)
			condition = self.condition.eval(ctx).std_out()'''

class Binary_Operation(Node):
	def __init__(self, left, right, op):
		self.left = left
		self.right = right
		self.op = op

	def eval(self, ctx):
		from interpreter import W_BinOp, W_StrObject, W_FloatObject

		if isinstance(self.left.eval(ctx), W_FloatObject) and isinstance(self.right.eval(ctx), W_FloatObject): 
			return W_BinOp(self.left.eval(ctx), self.right.eval(ctx), self.op).gen_ans()

		elif isinstance(self.left.eval(ctx), W_StrObject) and isinstance(self.right.eval(ctx), W_StrObject): 
			return W_BinOp(self.left.eval(ctx).lookup(ctx), self.right.eval(ctx).lookup(ctx), self.op).gen_ans()

		elif isinstance(self.left.eval(ctx), W_StrObject) and isinstance(self.right.eval(ctx), W_FloatObject): 
			return W_BinOp(self.left.eval(ctx).lookup(ctx), self.right.eval(ctx), self.op).gen_ans()

		elif isinstance(self.left.eval(ctx), W_FloatObject) and isinstance(self.right.eval(ctx), W_StrObject): 
			return W_BinOp(self.left.eval(ctx), self.right.eval(ctx).lookup(ctx), self.op).gen_ans()

class List(Node):
	def __init__(self):
		pass

class ListOp(Node):
	def __init__(self, list_name, new_value):
		self.list_name = list_name
		self.new_value = new_value

	def eval(self, ctx):
		#print self.new_value.eval(ctx)
		from interpreter import W_ListObject, W_StrObject, W_FloatObject
		try:
			if (ctx.env[self.list_name], W_ListObject):
				if isinstance(self.new_value.eval(ctx), W_FloatObject):
					ctx.env[self.list_name].append(self.new_value.eval(ctx))
				elif isinstance(self.new_value.eval(ctx), W_StrObject):
					ctx.env[self.list_name].append(self.new_value.eval(ctx).lookup(ctx))
					#print self.new_value.eval(ctx).lookup(ctx)

		except KeyError as e:
			print "Cannot append to non-existent list: ", e

class Function(Node):
	def __init__(self, func_name, arglist, func_statements):
		self.func_name = func_name
		self.func_statements = func_statements
		self.arglist = arglist

	def eval(self, ctx):
		#print self.func_statements #self.func_statements returns a block object
		func_details = (self.func_name, self.arglist, self.func_statements)
		ctx.func_list.append(func_details)
		#Makes function details and pushes them to the function list

class FunctionCall(Node):
	def __init__(self, func_name, func_arguments):
		self.func_name = func_name
		self.func_arguments = func_arguments

	def eval(self, ctx):
		#At this point i'm clearly inside a function
		#You can parse another ctx at this point
		#The best solution would be to parse another
		from interpreter import local_scope
		l_env = local_scope()

		if self.func_arguments is None:
			if len(ctx.func_list) > 0:
				for defined_function in ctx.func_list:
					if self.func_name == defined_function[0]:
						defined_function[2].eval(l_env)

		elif self.func_arguments is not None:
			#print self.func_arguments.getastlist()
			#compare the number of arguments to the actual number of arguments the function should take
			for defined_function in ctx.func_list:
				if self.func_name == defined_function[0]:
					if len(defined_function[1].getastlist()) == len(self.func_arguments.getastlist()):
						#Sort out all the arguments
						arg_values = self.func_arguments.getastlist(); arg_names = defined_function[1].getastlist()

						pos = 0
						for name in arg_names:
							name = name.eval(l_env).strval

							if isinstance(arg_values[pos], Id):
								value = arg_values[pos].eval(l_env).lookup(ctx)
								l_env.env[name] = value
							elif isinstance(arg_values[pos], Number):
								value = arg_values[pos].eval(l_env)
								l_env.env[name] = value
							
							#l_env.env[name] = value
							pos += 1

						#Execute all the inside statements
						defined_function[2].eval(l_env)
					else:
						print "Unequal number of arguments"
						#This should break the interpretation and end 
			

		#This then should access the function list, check for the function name
		#and perform the operations in the function

		#Two seprate branches, functions with arguments and functions without arguments
		#pass

def jitpolicy(driver):
    from pypy.jit.codewriter.policy import JitPolicy
    return JitPolicy()


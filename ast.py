from rply.token import BaseBox
from rpython.rlib.jit import JitDriver, promote

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
			returns.eval(ctx)

class Number(Node):
	def __init__(self, value):
		self.value = value

	def eval(self, ctx):
		from interpreter import W_IntObject
		return W_IntObject(self.value)
		
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
		if isinstance(self.expression, Id):
			try: 
				reverse_ident = ctx.env[self.expression.eval(ctx).strval]
				ctx.env[self.lvalue.eval(ctx).strval] = reverse_ident
			except KeyError as e:
				#raise Exception('Undefined assignment!')
				raise KeyError(': ' + str(e))

		elif isinstance(self.expression, Number):
			ctx.env[self.lvalue.eval(ctx).strval] = self.expression.eval(ctx).r_self()

		elif isinstance(self.expression, String):
			ctx.env[self.lvalue.eval(ctx).strval] = self.expression.eval(ctx).r_self()			

		elif isinstance(self.expression, Binary_Operation) == True:
			ctx.env[self.lvalue.eval(ctx).strval] = self.expression.eval(ctx).r_self()

		elif isinstance(self.expression, ClassOp):
			if self.expression.eval(ctx) is not None:
				ctx.env[self.lvalue.eval(ctx).strval] = self.expression.eval(ctx).r_self()
			else: #Write a better check
				method_name = "instance_"
				method_name += self.expression.ret_ins_name().strval
				method_name += "()"

				try:
					return_val = ctx.env[method_name]
					ctx.env[self.lvalue.eval(ctx).strval] = return_val
				except KeyError as e:
					raise KeyError(': ' + str(e))

		elif isinstance(self.expression, Call):
			#Since function is getting assigned execute function before assignment
			#Doesn't currently check if function has a return statement or not.
			if self.expression.r_name().strval in ctx.class_list:
				ctx.class_objects[self.lvalue.eval(ctx).strval] = ctx.class_list[self.expression.r_name().strval]
				self.expression.eval(ctx) #This calls the class_eval function in Call
			else: 
				self.expression.eval(ctx)
				call = self.expression
				
				func_name = call.r_name().strval
				func_name += "()"
				try:
					return_val = ctx.env[func_name]
					ctx.env[self.lvalue.eval(ctx).strval] = return_val
				except KeyError as e:
					raise KeyError(': ' + str(e))
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

	def ret_lval(self):
		return self.lvalue

class Print(Node):
	def __init__(self, expression):
		self.expression = expression

	def eval(self, ctx):
		#print self.expression
		if isinstance(self.expression, String):
			#Direct Output
			print self.expression.eval(ctx).strval

		elif isinstance(self.expression, Binary_Operation):
			#Direct Output
			print self.expression.eval(ctx).std_out()

		elif isinstance(self.expression, Condition):
			#Direct Output
			print self.expression.eval(ctx).std_out()

		elif isinstance(self.expression, Id):
			try:
				output = ctx.env[self.expression.eval(ctx).strval]

				from interpreter import W_StrObject, W_ListObject, W_IntObject
				if isinstance(output, W_IntObject) or isinstance(output, W_StrObject) or isinstance(output, W_IntObject):
					#Direct Output
					print output.std_out()
				elif isinstance(output, W_ListObject):
					list_values = []
					for value in output.f_list:
						if isinstance(value, W_IntObject):
							list_values.append(value.intval)
					#Direct Output
					print list_values

			except KeyError as e:
				raise KeyError(': ' + str(e))

class Condition(Node):
	def __init__(self, lvalue, cmp_op, rvalue):
		self.lvalue = lvalue
		self.cmp_op = cmp_op
		self.rvalue = rvalue
	
	def eval(self, ctx):
		from interpreter import W_BoolObject, W_IntObject, W_StrObject

		if isinstance(self.lvalue.eval(ctx), W_IntObject) and isinstance(self.rvalue.eval(ctx), W_IntObject):
			return W_BoolObject(self.lvalue.eval(ctx).intval, self.cmp_op, self.rvalue.eval(ctx).intval).return_val()

		elif isinstance(self.lvalue.eval(ctx), W_StrObject) and isinstance(self.rvalue.eval(ctx), W_StrObject):
			return W_BoolObject(self.lvalue.eval(ctx).lookup(ctx).intval, self.cmp_op, self.rvalue.eval(ctx).lookup(ctx).intval).return_val()

		elif isinstance(self.lvalue.eval(ctx), W_StrObject) and isinstance(self.rvalue.eval(ctx), W_IntObject):
			return W_BoolObject(self.lvalue.eval(ctx).lookup(ctx).intval, self.cmp_op, self.rvalue.eval(ctx).intval).return_val()
		
		elif isinstance(self.lvalue.eval(ctx), W_IntObject) and isinstance(self.rvalue.eval(ctx), W_StrObject):
			return W_BoolObject(self.lvalue.eval(ctx).intval, self.cmp_op, self.rvalue.eval(ctx).lookup(ctx).intval).return_val()

class If(Node):
	def __init__(self, condition, ifstatements, elsestatements):
		self.condition = condition
		self.ifstatements = ifstatements
		self.elsestatements = elsestatements

	def eval(self, ctx):
		if self.elsestatements is None:
			if self.condition.eval(ctx).std_out() == 'True':
				intern_states = self.ifstatements.getastlist()
				for nodes in intern_states:
					nodes.eval(ctx)
			elif self.condition.eval(ctx).std_out() == 'False':
				pass
		elif isinstance(self.elsestatements, Block):
			if self.condition.eval(ctx).std_out() == 'True':
				for nodes in self.ifstatements.getastlist():
					nodes.eval(ctx)
			elif self.condition.eval(ctx).std_out() == 'False':
				for nodes in self.elsestatements.getastlist():
					nodes.eval(ctx)

jitdriver = JitDriver(greens=['self'], reds=['ctx'])
#Greens - Constant || Reds - Not constant

class While(Node):
	def __init__(self, condition, statements):
		self.condition = condition
		self.statements = statements

	def eval(self, ctx):
		promote(self.statements)
		while True:	
			jitdriver.jit_merge_point(self=self, ctx=ctx)

			if not self.condition.eval(ctx).std_out() is 'True':
				break

			self.statements.eval(ctx)
			jitdriver.can_enter_jit(self=self, ctx=ctx)

class Binary_Operation(Node):
	def __init__(self, left, right, op):
		self.left = left
		self.right = right
		self.op = op

	def eval(self, ctx):
		from interpreter import W_BinOp, W_StrObject, W_IntObject

		if isinstance(self.left.eval(ctx), W_IntObject) and isinstance(self.right.eval(ctx), W_IntObject): 
			return W_BinOp(self.left.eval(ctx), self.right.eval(ctx), self.op).gen_ans()

		elif isinstance(self.left.eval(ctx), W_StrObject) and isinstance(self.right.eval(ctx), W_StrObject): 
			return W_BinOp(self.left.eval(ctx).lookup(ctx), self.right.eval(ctx).lookup(ctx), self.op).gen_ans()

		elif isinstance(self.left.eval(ctx), W_StrObject) and isinstance(self.right.eval(ctx), W_IntObject): 
			return W_BinOp(self.left.eval(ctx).lookup(ctx), self.right.eval(ctx), self.op).gen_ans()

		elif isinstance(self.left.eval(ctx), W_IntObject) and isinstance(self.right.eval(ctx), W_StrObject): 
			return W_BinOp(self.left.eval(ctx), self.right.eval(ctx).lookup(ctx), self.op).gen_ans()

class List(Node):
	def __init__(self):
		pass

class ListOp(Node):
	def __init__(self, list_name, new_value):
		self.list_name = list_name
		self.new_value = new_value

	def eval(self, ctx):
		from interpreter import W_ListObject, W_StrObject, W_IntObject
		try:
			if (ctx.env[self.list_name], W_ListObject):
				if isinstance(self.new_value.eval(ctx), W_IntObject):
					ctx.env[self.list_name].append(self.new_value.eval(ctx))
				elif isinstance(self.new_value.eval(ctx), W_StrObject):
					ctx.env[self.list_name].append(self.new_value.eval(ctx).lookup(ctx))

		except KeyError as e:
			raise KeyError(': ' + str(e))


class Function(Node):
	def __init__(self, func_name, arglist, func_statements):
		self.func_name = func_name
		self.func_statements = func_statements
		self.arglist = arglist

	def eval(self, ctx):
		func_details = (self.func_name, self.arglist, self.func_statements)
		ctx.func_list.append(func_details)
		#Makes function details and pushes them to the function list

	def method_eval(self, class_env):
		func_details = (self.func_name, self.arglist, self.func_statements)
		class_env.func_list.append(func_details)
		#Makes function details and pushes them to the function list

class Return(Node):
	def __init__(self, return_val):
		self.return_val = return_val

	def eval(self, ctx):
		pass

class Call(Node):
	def __init__(self, func_name, func_arguments):
		self.func_name = func_name
		self.func_arguments = func_arguments

	def function_eval(self, ctx):
		from interpreter import local_scope
		l_env = local_scope()

		#functions without arguments
		if self.func_arguments is None:
			if len(ctx.func_list) > 0:
				for defined_function in ctx.func_list:
					if self.func_name == defined_function[0]:
						#Return statement
						for statement in defined_function[2].getastlist():
							if not isinstance(statement, Return):
								statement.eval(l_env)
							else:
								if isinstance(statement.return_val, Id):
									ctx.env[self.func_name + "()"] = statement.return_val.eval(l_env).lookup(l_env)
								elif isinstance(statement.return_val, Number):
									if statement.return_val.eval(l_env).std_out() == '0':
										return
									elif statement.return_val.eval(l_env).std_out() == '1':
										return
								elif isinstance(statement.return_val, String):
									ctx.env[self.func_name + "()"] = statement.return_val.eval(l_env)
					else:
						raise NameError('name \'' + self.func_name + '\' is not defined')
			else:
				raise NameError('name \'' + self.func_name + '\' is not defined')
		#Functions with arguments
		elif self.func_arguments is not None:
			#compare the number of arguments to the actual number of arguments the function should take
			for defined_function in ctx.func_list:
				if self.func_name == defined_function[0] and defined_function[1] is not None:
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
						
							pos += 1

						#Execute all the inside statements
						for statement in defined_function[2].getastlist():
							if not isinstance(statement, Return):
								statement.eval(l_env)
							else:
								if isinstance(statement.return_val, Id):
									ctx.env[self.func_name + "()"] = statement.return_val.eval(l_env).lookup(l_env)
								elif isinstance(statement.return_val, Number):
									if statement.return_val.eval(l_env).std_out() == '0':
										return
									elif statement.return_val.eval(l_env).std_out() == '1':
										return
								elif isinstance(statement.return_val, String):
									ctx.env[self.func_name + "()"] = statement.return_val.eval(l_env)
						
					else:
						raise NameError('name \'' + self.func_name + '\' is not defined')

				else:
					raise AttributeError('name \'' + self.func_name + '\' is not defined')

	def class_eval(self, ctx):
		pass

	def eval(self, ctx):
		if self.func_name in ctx.class_list:
			self.class_eval(ctx)
		else: 
			self.function_eval(ctx)
		
	def r_name(self):
		from interpreter import W_StrObject
		return W_StrObject(self.func_name)

class Class(Node):
	def __init__(self, class_name, class_content):
		self.class_name = class_name
		self.class_content =class_content

	def eval(self, ctx):
		attributes = []; methods = []

		for details in self.class_content.getastlist():
			if not isinstance(details, Function):
				attributes.append(details)
			elif isinstance(details, Function):
				methods.append(details)
		
		class_details = (attributes, methods)

		ctx.class_list[self.class_name] = class_details

class ClassOp(Node):
	def __init__(self, instance_name, instance_attrib, instance_method, r_value, func_arguments):
		self.instance_name = instance_name
		self.instance_attrib = instance_attrib 
		self.instance_method = instance_method
		self.r_value = r_value
		self.func_arguments = func_arguments

	def update_class_env(self, ctx, class_env):
		try:
			object_details = ctx.class_objects[self.instance_name]
			attribute_list = object_details[0]

			for attrib in attribute_list:
				attrib.eval(class_env)

		except KeyError as e:
			raise KeyError(': ' + str(e))

	def update_method_env(self, ctx, class_env):
		try:
			instance_methods = ctx.class_objects[self.instance_name][1]
				
			for method in instance_methods:
				method.method_eval(class_env)

		except KeyError as e:
			raise KeyError(': ' + str(e))

	def eval(self, ctx):
		from interpreter import class_scope
		class_env = class_scope()
		
		#Handles attribute calls
		if (self.instance_attrib is not None) and (self.r_value is None):
			#Recreate the entire entity and push it to that space
			self.update_class_env(ctx, class_env)		

			#Check instance has that attribute!
			if self.instance_attrib.eval(ctx).std_out() in class_env.env:
				return class_env.env[self.instance_attrib.eval(ctx).std_out()]
		
		#Handles instance calls
		elif (self.instance_method is not None) and (self.r_value is None):
			self.update_class_env(ctx, class_env)

			self.update_method_env(ctx, class_env)
	
			for method in class_env.func_list:
				#handles methods without arguments
				if (method[0] == self.instance_method) and (method[1] is None):
					for statement in method[2].getastlist():
						if not isinstance(statement, Return):
							statement.eval(class_env)
						else:
							if isinstance(statement.return_val, Id):
								ctx.env["instance_" + self.instance_name + "()"] = statement.return_val.eval(class_env).lookup(class_env)
							elif isinstance(statement.return_val, Number):
								if statement.return_val.eval(class_env).std_out() == '0':
									return
								elif statement.return_val.eval(class_env).std_out() == '1':
									return
							elif isinstance(statement.return_val, String):
								ctx.env["instance_" + self.instance_name + "()"] = statement.return_val.eval(class_env)

				#Handles methods with arguments
				elif (method[0] == self.instance_method) and (method[1] is not None):
					
					arg_values = self.func_arguments.getastlist(); arg_names = method[1].getastlist()

					pos = 0
					for name in arg_names:
						name = name.eval(class_env).strval

						if isinstance(arg_values[pos], Id):
							value = arg_values[pos].eval(class_env).lookup(ctx)
							class_env.env[name] = value
						elif isinstance(arg_values[pos], Number):
							value = arg_values[pos].eval(class_env)
							class_env.env[name] = value
						
						pos += 1

					#Execute all the inside statements
					for statement in method[2].getastlist():
						if not isinstance(statement, Return):
							statement.eval(class_env)
						else:
							if isinstance(statement.return_val, Id):
								ctx.env["instance_" + self.instance_name + "()"] = statement.return_val.eval(class_env).lookup(class_env)
							elif isinstance(statement.return_val, Number):
								if statement.return_val.eval(class_env).std_out() == '0':
									return
								elif statement.return_val.eval(class_env).std_out() == '1':
									return
							elif isinstance(statement.return_val, String):
								ctx.env["instance_" + self.instance_name + "()"] = statement.return_val.eval(class_env)				
						
		#Handles attribute assignments
		elif self.r_value is not None:
			position = 0

			try:
				object_details = ctx.class_objects[self.instance_name]
				attribute_list = object_details[0]

				p = 0 
				for attrib in attribute_list:
					if attrib.ret_lval().eval(ctx).std_out() == self.instance_attrib.eval(ctx).std_out():
						position = p
					p += 1

				ctx.class_objects[self.instance_name][0][position] = Assignment(self.instance_attrib, self.r_value)
			except KeyError as e:
				raise KeyError(': ' + str(e))

	def ret_ins_name(self):
		from interpreter import W_StrObject
		return W_StrObject(self.instance_name)

def jitpolicy(driver):
    from pypy.jit.codewriter.policy import JitPolicy
    return JitPolicy()
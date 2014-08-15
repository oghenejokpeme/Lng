from rply import ParserGenerator
from lexer import lexer
from ast import *

pg = ParserGenerator(
	[rule.name for rule in lexer.rules],
	precedence = [
		('left', ['PLUS', 'MINUS']), 
        ('left', ['MULT','DIVIDE']),
        ('left', 'EQUALS')
	],
	cache_id = 'program',
)

@pg.production('main : statements')
def main(p):
	return p[0]

@pg.production('statements : statements statement')
def statements(p):
	return Block(p[0].getastlist() + [p[1]])

@pg.production('statements : statement')
def statements(p):
	return Block([p[0]])

@pg.production('statement : expression')
def statement_expression(p):
	return p[0]

@pg.production('expression : ID')
def identifier(p):
	return Id(p[0].getstr())

@pg.production('expression : NUMBER')
def expression_number(p):
	return Number(int(p[0].getstr()))
	
@pg.production('expression : STRING')
def expression_string(p):
	return String(p[0].getstr())

@pg.production('statement : LBRACKET statements RBRACKET')
@pg.production('statement : LBRACKET RBRACKET')
def expression_list(p):
	if len(p) == 3:
		return p[1]
	elif len(p) == 2:
		return List()

@pg.production('statement : ID PERIOD APPEND LPAREN expression RPAREN')
def expressoin_list_operation(p):
	list_name, _, _, _, value, _ = p
	return ListOp(list_name.getstr(), value)

@pg.production('statement : PRINT statement')
def print_statement(p):
	return Print(p[1])

@pg.production('expression : expression PLUS expression')
@pg.production('expression : expression DIVIDE expression')
@pg.production('expression : expression MINUS expression')
@pg.production('expression : expression MULT expression')
def expression_binary_operation(p):
	left = p[0]
	right = p[2]
	op = p[1]
	if p[1].gettokentype() == 'PLUS' or 'DIVIDE' or 'MINUS' or 'MULT':
		return Binary_Operation(left, right, op.getstr())

@pg.production('statement : expression ASSIGN statement')
def assignment_statement(p):
	lvalue, _, expression = p
	return Assignment(lvalue, expression)

@pg.production('statement : expression CMP expression')
def conditional_statement(p):
	lvalue, cmp_op, rvalue = p
	return Condition(lvalue, cmp_op.getstr(), rvalue) 

@pg.production('statement : IF statement LBRACE statements RBRACE')
def if_statement(p):
	_, condition, _, ifstatements, _ = p
	return If(condition, ifstatements, None)

@pg.production('statement : IF statement LBRACE statements RBRACE ELSE LBRACE statements RBRACE')
def ifelse_statement(p):
	_, condition, _, ifstatements, _, _, _, elsestatements, _ = p
	return If(condition, ifstatements, elsestatements)

@pg.production('statement : WHILE statement LBRACE statements RBRACE')
def while_statement(p):
	_, condition, _, statements, _ = p
	return While(condition, statements)

@pg.production('statement : RETURN statement')
def return_statement(p):
	return Return(p[1])

@pg.production('statement : DEF ID LPAREN RPAREN LBRACE statements RBRACE')
@pg.production('statement : DEF ID LPAREN statements RPAREN LBRACE statements RBRACE')
def function_def(p):
	if len(p) == 7:
		_, func_name, _, _, _, func_statements, _ = p 
		return Function(func_name.getstr(), None, func_statements)
	elif len(p) == 8:
		_, func_name, _, arglist, _, _, func_statements, _ = p
		return Function(func_name.getstr(), arglist, func_statements) 


@pg.production('statement : ID LPAREN RPAREN')
@pg.production('statement : ID LPAREN statements RPAREN')
def function_call(p):
	if len(p) == 3:
		return Call(p[0].getstr(), None)
	elif len(p) == 4:
		return Call(p[0].getstr(), p[2])

@pg.production('statement : CLASS ID LPAREN RPAREN LBRACE statements RBRACE')
def class_definition(p):
	_, class_name, _, _, _, class_content, _ = p
	return Class(class_name.getstr(), class_content)

@pg.production('statement : ID PERIOD ID')
@pg.production('statement : ID PERIOD ID LPAREN RPAREN')
@pg.production('statement : ID PERIOD ID LPAREN statements RPAREN')
def expression_list_operation(p):
	if len(p) == 3:
		instance_name, _, instance_attrib = p
		return ClassOp(instance_name.getstr(), Id(instance_attrib.getstr()), None, None, None)
	elif len(p) == 5 and p[3].getstr() == '(':
		instance_name, _, instance_method, _, _ = p
		return ClassOp(instance_name.getstr(), None, instance_method.getstr(), None, None)
	elif len(p) == 6:
		instance_name, _, instance_method, _, method_arguments,_ = p
		return ClassOp(instance_name.getstr(), None, instance_method.getstr(), None, method_arguments)


@pg.production('statement : ID PERIOD ID ASSIGN expression')
def class_attrib_assign(p):
	instance_name, _, attrib_name, _, rvalue = p
	return ClassOp(instance_name.getstr(), Id(attrib_name.getstr()), None, rvalue, None)

parser = pg.build()

def parse(source):
	return parser.parse(lexer.lex(source))
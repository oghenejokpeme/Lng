from rply import ParserGenerator

from lexer import lexer
from ast import *
#from ast_bckp import *
from lexer import test_lex

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
	#return Statement(p[0])

@pg.production('expression : ID')
def identifier(p):
	#print p[0].getstr()
	return Id(p[0].getstr())

@pg.production('expression : NUMBER')
def expression_number(p):
	return Number(float(p[0].getstr()))
	
@pg.production('expression : STRING')
def expression_string(p):
	return String(p[0].getstr())

@pg.production('statement : LBRACKET statements RBRACKET')
@pg.production('statement : LBRACKET RBRACKET')
def expression_list(p):
	#p[1] Returns a Block object of everything in the braces
	if len(p) == 3:
		return p[1]
	elif len(p) == 2:
		return List() #Returns an empty list, used this to handled instantiation of empty list

@pg.production('statement : ID PERIOD expression LPAREN expression RPAREN')
def expressoin_list_operation(p):
	#x->(6)
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

@pg.production('statement : DEF ID LPAREN RPAREN LBRACE statements RBRACE')
@pg.production('statement : DEF ID LPAREN statements RPAREN LBRACE statements RBRACE')
def function_def(p):
	if len(p) == 7:
		_, func_name, _, _, _, func_statements, _ = p 
		#print func_name, func_statements
		return Function(func_name.getstr(), None, func_statements)
	elif len(p) == 8:
		_, func_name, _, arglist, _, _, func_statements, _ = p
		return Function(func_name.getstr(), arglist, func_statements) 


@pg.production('statement : ID LPAREN RPAREN')
def function_call(p):
	if len(p) == 3:
		#print p[0].getstr()
		return FunctionCall(p[0].getstr())

parser = pg.build()

def parse(source):
	#test_lex(source)
	#return parser.parse(lexer.lex(source)).eval()
	return parser.parse(lexer.lex(source))
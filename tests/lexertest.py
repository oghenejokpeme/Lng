import Lng.lexer

#Keywords
def test_PRINT():
	assert lexer.test_lex("print") == Token('PRINT', 'print')

def test_IF():
	assert lexer.test_lex("if") == Token('IF', 'if')

def test_ELSE():
	assert lexer.test_lex("else") == Token('ELSE', 'else')

def test_WHILE():
	assert lexer.test_lex("while") == Token('WHILE', 'while')

def test_DEF():
	assert lexer.test_lex("def") == Token('DEF', 'def')

def test_APPEND():
	assert lexer.test_lex("append") == Token('APPEND', 'append')

def test_CLASS():
	assert lexer.test_lex("class") == Token('CLASS', 'class')

def test_ASSIGN():
	assert lexer.test_lex("=") == Token('ASSIGN', '=')

def test_RETURN():
	assert lexer.test_lex("return") == Token('RETURN', 'return')

#Mathematical Operators
def test_PLUS():
	assert lexer.test_lex("+") == Token('PLUS', '+')

def test_MINUS():
	assert lexer.test_lex("-") == Token('MINUS', '-')

def test_MULT():
	assert lexer.test_lex("*") == Token('MULT', '*')

def test_DIVIDE():
	assert lexer.test_lex("/") == Token('DIVIDE', '/')

def test_PERIOD():
	assert lexer.test_lex(".") == Token('PERIOD', '.')

#Comparison Operators
def test_CMP():
	assert lexer.test_lex(">=") == Token('CMP', '>=')
	assert lexer.test_lex("<=") == Token('CMP', '<=')
	assert lexer.test_lex("<>") == Token('CMP', '<>')
	assert lexer.test_lex(">") == Token('CMP', '>')
	assert lexer.test_lex("<") == Token('CMP', '<')
	assert lexer.test_lex("!=") == Token('CMP', '!=')

#Grouping
def test_LBRACE():
	assert lexer.test_lex("{") == Token('LBRACE', '{')

def test_RBRACE():
	assert lexer.test_lex("}") == Token('RBRACE', '}')

def test_LPAREN():
	assert lexer.test_lex("(") == Token('LPAREN', '(')

def test_RPAREN():
	assert lexer.test_lex(")") == Token('RPAREN', ')')

def test_LBRACKET():
	assert lexer.test_lex("[") == Token('LBRACKET', '[')

def test_RBRACKET():
	assert lexer.test_lex("]") == Token('RBRACKET', ']')

def test_STRING():
	assert lexer.test_lex("\"String!\"") == Token('STRING', '\"String!\"')

def test_NUMBER():
	assert lexer.test_lex("80") == Token('NUMBER', '80')

def test_ID():
	assert lexer.test_lex("identifier") == Token('ID', 'identifier')
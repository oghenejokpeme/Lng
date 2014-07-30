from rply import LexerGenerator

lg = LexerGenerator()

#Keywords
lg.add('PRINT', 'print')
lg.add('IF', r'if')
lg.add('ELSE', r'else')
lg.add('WHILE', r'while')
lg.add('DEF', r'def')
lg.add('APPEND', r'append')
lg.add('CLASS', r'class')
lg.add('ASSIGN', r'=')

lg.add('RETURN', r'return')

#Mathematical Operators
lg.add('PLUS', r'\+')
lg.add('MINUS', r'-')
lg.add('MULT', r'\*')
lg.add('DIVIDE', r'/')
lg.add('PERIOD', r'\.')
#lg.add('OP', r'\+|\-|\*|\/')

#Comparison op
lg.add('CMP', r'(\>=)|(\<=)|(<>)|(>)|(<)|(!=)')

#Grouping
lg.add('LBRACE', r'\{')
lg.add('RBRACE', r'\}')
lg.add('LPAREN', r'\(')
lg.add('RPAREN', r'\)')
lg.add('LBRACKET', r'\[')
lg.add('RBRACKET', r'\]')
lg.add('STRING', r'([\"\'])(?:(?=(\\?))\2.)*?\1')

#Number literals
lg.add('NUMBER', r'(?:\d*\.)?\d+')

#Identifiers
lg.add('ID', r'[a-zA-Z_][a-zA-Z_0-9_]*')

#Ignore
lg.ignore(r'\s+')
lg.ignore(r'\n')
lg.ignore(r'\t')
lg.ignore(r'\#.*')

lexer = lg.build()

def lex(source):
    stream = lexer.lex(source)

    tok = stream.next()
    while tok is not None:
        yield tok
        tok = stream.next()

def test_lex(source):
    code = []
    tokens = lexer.lex(source)

    for tok in tokens:
        code.append(tok)
        print tok
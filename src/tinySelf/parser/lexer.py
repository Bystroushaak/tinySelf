# -*- coding: utf-8 -*-
from rply import LexerGenerator


lg = LexerGenerator()
lg.ignore(r'\s+')

lg.add('SELF', r'self')

lg.add('NUMBER', r'((\-)?\d+(\.\d)?)|(\\x[0-9a-fA-F]+)')

lg.add('OBJ_START', r'\(')
lg.add('OBJ_END', r'\)')

lg.add('BLOCK_START', r'\[')
lg.add('BLOCK_END', r'\]')

lg.add('SINGLE_Q_STRING', r"'(?:\\.|[^'\\])*'")
lg.add('DOUBLE_Q_STRING', r'"(?:\\.|[^"\\])*"')

lg.add('FIRST_KW', r'[a-z_]+[a-zA-Z0-9_]*:')
lg.add('KEYWORD', r'[A-Z]+[a-zA-Z0-9_]*:')
lg.add('ARGUMENT', r':[a-zA-Z_]*[a-zA-Z0-9_]+')

lg.add('RW_ASSIGNMENT', r'\<-')

lg.add('OPERATOR', r'[!@\$%&\*\-\+~/?<>,]+|==+')
lg.add('RETURN', r'\^')
lg.add('END_OF_EXPR', r'\.')
lg.add('SEPARATOR', r'\|')
lg.add('CASCADE', r'\;')

lg.add('IDENTIFIER', r'[a-zA-Z_]*[a-zA-Z0-9_\*]+')

lg.add('ASSIGNMENT', r'=')

lg.add('COMMENT', r'#.*[\n|$]?')


lexer = lg.build()

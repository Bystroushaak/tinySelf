#! /usr/bin/env python2
#
# https://rpython.readthedocs.io/en/latest/rlib.html#ebnf
# 
from rply import LexerGenerator


lg = LexerGenerator()


lg.add('INTEGER', '-?\d+')
lg.add('FLOAT', '-?\d+\.\d+')
# lg.add('STRING', '(""".?""")|(".?")|(\'.?\')|(\'\'\'.?\'\'\')')
lg.add('IDENTIFIER', "[a-zA-Z_]+[a-zA-Z0-9_]*")
lg.add('DOT', '\.')
lg.add('|', '\|')
lg.add('(', '\(')
lg.add(')', '\)')
lg.add('[', '\[')
lg.add(']', '\]')
lg.add('{', '\{')
lg.add('}', '\}')
lg.add('NEWLINE', '\n')


# ignore whitespace 
lg.ignore('[ \t\r\f\v]+')

lexer = lg.build()


print list(lexer.lex("azgabash."))
# list(lexer.lex("let a = 5"))
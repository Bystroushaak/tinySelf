#! /usr/bin/env pypy
# -*- coding: utf-8 -*-
#
# Interpreter version: pypy 2.7
#
from rply import LexerGenerator


lg = LexerGenerator()
lg.ignore(r'\s+')

lg.add('NUMBER', r'\d+')

lg.add('OPEN_PAREN', r'\(')
lg.add('CLOSE_PAREN', r'\)')

lg.add('OPEN_BRACKET', r'\[')
lg.add('CLOSE_BRACKET', r'\]')

lg.add('SINGLE_Q_STRING', r"'(?:\\.|[^'\\])*'")
lg.add('DOUBLE_Q_STRING', r'"(?:\\.|[^"\\])*"')

lg.add('KEYWORD', r'[A-Z]+[a-zA-Z0-9_]*:')
lg.add('FIRST_KW', r'[a-z_]+[a-zA-Z0-9_]*:')
lg.add('ARGUMENT', r':[a-zA-Z0-9_]*[a-zA-Z0-9_]+')
lg.add('IDENTIFIER', r'[a-zA-Z0-9_]*[a-zA-Z0-9_]+')

lg.add('OPERATOR', r'[!@#\$%&\*\-\+=~/?<>,;]')
lg.add('RETURN', r'\^')
lg.add('END_OF_EXPR', r'\.')

l = lg.build()

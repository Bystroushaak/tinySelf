#! /usr/bin/env pypy
# -*- coding: utf-8 -*-
#
# Interpreter version: pypy 2.7
#
from rply import LexerGenerator


lg = LexerGenerator()
lg.ignore(r'\s+')

lg.add('NUMBER', r'\d+')

lg.add('PLUS', r'\+')
lg.add('MINUS', r'-')

lg.add('OPEN_PARENS', r'\(')
lg.add('CLOSE_PARENS', r'\)')

lg.add('SINGLE_Q_STRING', r"'(?:\\.|[^'\\])*'")
lg.add('DOUBLE_Q_STRING', r'"(?:\\.|[^"\\])*"')

l = lg.build()

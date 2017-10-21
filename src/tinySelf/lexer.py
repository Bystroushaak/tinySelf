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

l = lg.build()

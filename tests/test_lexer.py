#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from rply import Token

from tinySelf import lexer


def test_simple():
    assert list(lexer.l.lex('1+1-1')) == [
        Token('NUMBER', '1'),
        Token('PLUS', '+'),
        Token('NUMBER', '1'),
        Token('MINUS', '-'),
        Token('NUMBER', '1'),
    ]

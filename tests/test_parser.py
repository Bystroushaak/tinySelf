#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from tinySelf.lexer import lexer
from tinySelf.parser import parser


def test_parse_number():
    parser.parse(lexer.lex('1 + 1'))

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


def test_single_q_string():
    assert list(lexer.l.lex("'hello'")) == [
        Token('SINGLE_Q_STRING', "'hello'"),
    ]

    assert list(lexer.l.lex("'hello \\' quote'")) == [
        Token('SINGLE_Q_STRING', "'hello \\' quote'"),
    ]

    assert list(lexer.l.lex("'a \\' b' 'c \\' d'")) == [
        Token('SINGLE_Q_STRING', r"'a \' b'"),
        Token('SINGLE_Q_STRING', r"'c \' d'"),
    ]

    assert list(lexer.l.lex("'hello \n quote'")) == [
        Token('SINGLE_Q_STRING', "'hello \n quote'"),
    ]


def test_double_q_string():
    assert list(lexer.l.lex('"hello"')) == [
        Token('DOUBLE_Q_STRING', '"hello"'),
    ]

    assert list(lexer.l.lex('"hello \\" quote"')) == [
        Token('DOUBLE_Q_STRING', '"hello \\" quote"'),
    ]

    assert list(lexer.l.lex('"a \\" b" "c \\" d"')) == [
        Token('DOUBLE_Q_STRING', r'"a \" b"'),
        Token('DOUBLE_Q_STRING', r'"c \" d"'),
    ]

    assert list(lexer.l.lex('"hello \n quote"')) == [
        Token('DOUBLE_Q_STRING', '"hello \n quote"'),
    ]


def test_identifier():
    assert list(lexer.l.lex('identifier')) == [
        Token('IDENTIFIER', 'identifier'),
    ]

    assert list(lexer.l.lex('iDentIfier ID2')) == [
        Token('IDENTIFIER', 'iDentIfier'),
        Token('IDENTIFIER', 'ID2'),
    ]


def test_argument():
    assert list(lexer.l.lex(':argument')) == [
        Token('ARGUMENT', ':argument'),
    ]

    assert list(lexer.l.lex('"string" :argument idenTifier')) == [
        Token('DOUBLE_Q_STRING', '"string"'),
        Token('ARGUMENT', ':argument'),
        Token('IDENTIFIER', 'idenTifier'),
    ]


def test_kw_identifier():
    assert list(lexer.l.lex('kwArgument: i')) == [
        Token('FIRST_KW', 'kwArgument:'),
        Token('IDENTIFIER', 'i'),
    ]


def test_kw():
    assert list(lexer.l.lex('kwArgument: i KeyWord: kw')) == [
        Token('FIRST_KW', 'kwArgument:'),
        Token('IDENTIFIER', 'i'),
        Token('KEYWORD', 'KeyWord:'),
        Token('IDENTIFIER', 'kw'),
    ]

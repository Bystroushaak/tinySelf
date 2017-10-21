#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from rply import Token

from tinySelf import lexer


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


def test_complex():
    assert list(lexer.l.lex('(kwArgument: i KeyWord: [id])')) == [
        Token('OBJ_START', '('),
        Token('FIRST_KW', 'kwArgument:'),
        Token('IDENTIFIER', 'i'),
        Token('KEYWORD', 'KeyWord:'),
        Token("BLOCK_START", '['),
        Token('IDENTIFIER', 'id'),
        Token("BLOCK_END", ']'),
        Token('OBJ_END', ')'),
    ]


def test_operator():
    assert list(lexer.l.lex('!')) == [
        Token('OPERATOR', '!'),
    ]

    assert list(lexer.l.lex('!@$%&*-+=~/?<>,')) == [
        Token('OPERATOR', '!'),
        Token('OPERATOR', '@'),
        Token('OPERATOR', '$'),
        Token('OPERATOR', '%'),
        Token('OPERATOR', '&'),
        Token('OPERATOR', '*'),
        Token('OPERATOR', '-'),
        Token('OPERATOR', '+'),
        Token('OPERATOR', '='),
        Token('OPERATOR', '~'),
        Token('OPERATOR', '/'),
        Token('OPERATOR', '?'),
        Token('OPERATOR', '<'),
        Token('OPERATOR', '>'),
        Token('OPERATOR', ','),
    ]

    assert list(lexer.l.lex('! @ $ % & * - + = ~ / ? < > ,')) == [
        Token('OPERATOR', '!'),
        Token('OPERATOR', '@'),
        Token('OPERATOR', '$'),
        Token('OPERATOR', '%'),
        Token('OPERATOR', '&'),
        Token('OPERATOR', '*'),
        Token('OPERATOR', '-'),
        Token('OPERATOR', '+'),
        Token('OPERATOR', '='),
        Token('OPERATOR', '~'),
        Token('OPERATOR', '/'),
        Token('OPERATOR', '?'),
        Token('OPERATOR', '<'),
        Token('OPERATOR', '>'),
        Token('OPERATOR', ','),
    ]


def test_return():
    assert list(lexer.l.lex('^')) == [
        Token('RETURN', '^'),
    ]

    assert list(lexer.l.lex('^xe.')) == [
        Token('RETURN', '^'),
        Token('IDENTIFIER', 'xe'),
        Token('END_OF_EXPR', '.'),
    ]


def test_end_of_expression():
    assert list(lexer.l.lex('.')) == [
        Token('END_OF_EXPR', '.'),
    ]

    assert list(lexer.l.lex('obj message.')) == [
        Token('IDENTIFIER', 'obj'),
        Token('IDENTIFIER', 'message'),
        Token('END_OF_EXPR', '.'),
    ]


def test_separator():
    assert list(lexer.l.lex('|')) == [
        Token('SEPARATOR', '|'),
    ]

    assert list(lexer.l.lex('(|var| obj message.)')) == [
        Token('OBJ_START', '('),
        Token('SEPARATOR', '|'),
        Token('IDENTIFIER', 'var'),
        Token('SEPARATOR', '|'),
        Token('IDENTIFIER', 'obj'),
        Token('IDENTIFIER', 'message'),
        Token('END_OF_EXPR', '.'),
        Token('OBJ_END', ')'),

    ]


def test_comment():
    assert list(lexer.l.lex('#\n')) == [
        Token('COMMENT', '#\n'),
    ]

    assert list(lexer.l.lex('obj message. # comment \n id #')) == [
        Token('IDENTIFIER', 'obj'),
        Token('IDENTIFIER', 'message'),
        Token('END_OF_EXPR', '.'),
        Token('COMMENT', '# comment \n'),
        Token('IDENTIFIER', 'id'),
        Token('COMMENT', '#'),
    ]


def test_cascade():
    assert list(lexer.l.lex(';')) == [
        Token('CASCADE', ';'),
    ]

    assert list(lexer.l.lex('obj message; message2.')) == [
        Token('IDENTIFIER', 'obj'),
        Token('IDENTIFIER', 'message'),
        Token('CASCADE', ';'),
        Token('IDENTIFIER', 'message2'),
        Token('END_OF_EXPR', '.'),
    ]

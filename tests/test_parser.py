#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from tinySelf.lexer import lexer
from tinySelf.parser import parser

from tinySelf.parser import Send
from tinySelf.parser import Number
from tinySelf.parser import String
from tinySelf.parser import Object
from tinySelf.parser import BinaryMessage


def parse_and_lex(i):
    return parser.parse(lexer.lex(i))


def test_parse_number():
    result = parse_and_lex('1')

    assert isinstance(result, Number)
    assert result.value == 1


def test_parse_string():
    result = parse_and_lex('"asd"')

    assert isinstance(result, String)
    assert result.value == "asd"

    result = parse_and_lex("'asd'")
    assert result.value == "asd"

    result = parse_and_lex('""')
    assert result.value == ""


def test_parse_object():
    result = parse_and_lex('()')

    assert isinstance(result, Object)
    assert result.slots == {}
    assert result.code == []


def test_parse_object_with_spaces():
    result = parse_and_lex('(    )')

    assert isinstance(result, Object)
    assert result.slots == {}
    assert result.code == []


def test_parse_binary_op():
    result = parse_and_lex('1 + 1')

    assert isinstance(result, Send)
    assert isinstance(result.obj, Number)
    assert isinstance(result.msg, BinaryMessage)
    assert isinstance(result.msg.parameter, Number)

    assert result.obj.value == 1
    assert result.msg.name == "+"
    assert result.msg.parameter.value == 1

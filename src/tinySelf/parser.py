#! /usr/bin/env pypy
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from rply import ParserGenerator
from rply.token import BaseBox

from lexer import lexer


class Object(BaseBox):
    def __init__(self, slots, code):
        self.slots = slots
        self.code = code


class Block(Object):
    pass


class Number(BaseBox):  # TODO: remove
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value


class Code(BaseBox):
    def __init__(self, message_sends):
        self.message_sends = message_sends


class Message(BaseBox):
    def __init__(self, name):
        self.name = name


class KeywordMessage(BaseBox):
    def __init__(self, signature, parameters):
        self.signature = signature
        self.parameters = parameters


class BinaryMessage(BaseBox):
    def __init__(self, name, parameter):
        self.name = name
        self.parameter = parameter


pg = ParserGenerator(
    [
        "NUMBER",
        "OBJ_START",
        "OBJ_END",
        "BLOCK_START",
        "BLOCK_END",
        "SINGLE_Q_STRING",
        "DOUBLE_Q_STRING",
        "KEYWORD",
        "FIRST_KW",
        "ARGUMENT",
        "IDENTIFIER",
        "OPERATOR",
        "RETURN",
        "END_OF_EXPR",
        "SEPARATOR",
        "CASCADE",
        "COMMENT",
    ],
    precedence=[
    ]
)


@pg.production('expression : NUMBER')
def expression_number(p):
    return Number(int(p[0].getstr()))


@pg.production('expression : expression OPERATOR expression')
def expression_operator(p):
    assert len(p) == 3, "Bad number of operands for %s!" % p[1]

    print p

    return p


parser = pg.build()

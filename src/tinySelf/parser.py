#! /usr/bin/env pypy
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from rply import ParserGenerator
from rply.token import BaseBox

from lexer import lexer

from ast_tokens import Object
from ast_tokens import Block
from ast_tokens import Number
from ast_tokens import String
from ast_tokens import Code
from ast_tokens import Message
from ast_tokens import KeywordMessage
from ast_tokens import BinaryMessage
from ast_tokens import Send
from ast_tokens import Self


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


@pg.production('expression : SINGLE_Q_STRING')
@pg.production('expression : DOUBLE_Q_STRING')
def expression_string(p):
    return String(p[0].getstr()[1:-1])


@pg.production('expression : IDENTIFIER')
def expression_unary_message(p):
    return Send(obj=Self(), msg=Message(p[0].getstr()))


@pg.production('expression : expression IDENTIFIER')
def expression_unary_message_to_expression(p):
    return Send(obj=p[0], msg=Message(p[1].getstr()))


@pg.production('expression : expression OPERATOR expression')
def expression_binary_message_to_expression(p):
    assert len(p) == 3, "Bad number of operands for %s!" % p[1]

    return Send(p[0], BinaryMessage(p[1].getstr(), p[2]))


@pg.production('expression : FIRST_KW expression')
def expression_keyword_message(p):
    return Send(obj=Self(), msg=KeywordMessage(p[0].getstr(), [p[1]]))


@pg.production('kwd : KEYWORD expression')
@pg.production('kwd : KEYWORD expression kwd')
def expression_keyword(p):
    if len(p) == 2:
        return p

    # flatten the nested lists
    tokens = [p[0], p[1]]
    for group in p[2:]:
        tokens.extend(group)

    return tokens


@pg.production('expression : FIRST_KW expression kwd')
def expression_keyword_message_with_parameters(p):
    signature = [p[0]]
    parameters = [p[1]]

    for cnt, token in enumerate(p[2]):
        if cnt % 2 == 0:
            signature.append(token)
        else:
            parameters.append(token)

    return Send(
        obj=Self(),
        msg=KeywordMessage(
            name="".join(token.getstr() for token in signature),
            parameters=parameters
        )
    )


@pg.production('expression : OBJ_START OBJ_END')
@pg.production('expression : OBJ_START SEPARATOR SEPARATOR OBJ_END')
def expression_empty_object(p):
    return Object()


@pg.production('expression : SEPARATOR SEPARATOR')
def expression_empty_slots(p):
    return {}


# @pg.production('expression : SEPARATOR SEPARATOR')
# def expression_slots(p):
#     return {}


# def parse_slots


# @pg.production('expression : OBJ_START SEPARATOR expression SEPARATOR OBJ_END')
# def expression_object_with_slots(p):
#     return Object(slots=p[2])


parser = pg.build()

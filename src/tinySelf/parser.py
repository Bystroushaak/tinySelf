#! /usr/bin/env pypy
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from rply import ParserGenerator
from rply.token import Token
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
        "RW_ASSIGNMENT",
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


# Number ######################################################################
@pg.production('expression : NUMBER')
def expression_number(p):
    return Number(int(p[0].getstr()))


# Strings #####################################################################
@pg.production('expression : SINGLE_Q_STRING')
@pg.production('expression : DOUBLE_Q_STRING')
def expression_string(p):
    return String(p[0].getstr()[1:-1])


# Unary messages ##############################################################
@pg.production('expression : IDENTIFIER')
def expression_unary_message(p):
    return Send(obj=Self(), msg=Message(p[0].getstr()))


@pg.production('expression : expression IDENTIFIER')
def expression_unary_message_to_expression(p):
    return Send(obj=p[0], msg=Message(p[1].getstr()))


# Binary messages #############################################################
@pg.production('expression : expression OPERATOR expression')
def expression_binary_message_to_expression(p):
    assert len(p) == 3, "Bad number of operands for %s!" % p[1]

    return Send(p[0], BinaryMessage(p[1].getstr(), p[2]))


# Keyword messages ############################################################
@pg.production('expression : FIRST_KW expression')
def expression_keyword_message(p):
    return Send(obj=Self(), msg=KeywordMessage(p[0].getstr(), [p[1]]))


@pg.production('expression : expression FIRST_KW expression')
def expression_keyword_message_to_obj(p):
    return Send(obj=p[0], msg=KeywordMessage(p[1].getstr(), [p[2]]))


@pg.production('kwd : KEYWORD expression')
def expression_keyword(p):
    return p


@pg.production('kwd : KEYWORD expression kwd')
def expresion_keyword_multiple(p):
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


@pg.production('expression : expression FIRST_KW expression kwd')
def expression_keyword_message_to_obj_with_parameters(p):
    signature = [p[1]]
    parameters = [p[2]]

    for cnt, token in enumerate(p[3]):
        if cnt % 2 == 0:
            signature.append(token)
        else:
            parameters.append(token)

    return Send(
        obj=p[0],
        msg=KeywordMessage(
            name="".join(token.getstr() for token in signature),
            parameters=parameters
        )
    )


# Slot definition #############################################################
@pg.production('slot_kwd : KEYWORD IDENTIFIER')
def slot_name_kwd_one(p):
    return p


@pg.production('slot_kwd : KEYWORD IDENTIFIER slot_kwd')
def slot_name_kwd_multiple(p):
    # flatten the nested lists
    tokens = [p[0], p[1]]
    for group in p[2:]:
        tokens.extend(group)

    return tokens


# @pg.production('slot_name : FIRST_KW IDENTIFIER slot_kwd')
# def slot_names_kwd(p):
#     pass


# @pg.production('slot_name : IDENTIFIER OPERATOR IDENTIFIER')
# def slot_names_operator(p):
    # pass


@pg.production('slot_name : IDENTIFIER')
def slot_names(p):
    return p[0].value


# @pg.production('slot_names : IDENTIFIER . slot_name')


@pg.production('slot_definition : slot_name')
def nil_slot_definition(p):
    return {p[0]: None}


@pg.production('slot_definition : slot_name RW_ASSIGNMENT expression')
def slot_definition(p):
    return {p[0]: p[2]}


@pg.production('slot_definition : slot_definition END_OF_EXPR')
@pg.production('slot_definition : slot_definition END_OF_EXPR slot_definition')
# @pg.production('slot_definition : slot_definition END_OF_EXPR slot_definition END_OF_EXPR')
def slots_definition(p):
    out = p[0]

    if len(p) >= 3:
        out.update(p[2])

    return out



# Object definition ###########################################################
@pg.production('expression : OBJ_START OBJ_END')
@pg.production('expression : OBJ_START SEPARATOR SEPARATOR OBJ_END')
def expression_empty_object(p):
    return Object()


@pg.production('expression : OBJ_START slot_definition SEPARATOR OBJ_END')
@pg.production('expression : OBJ_START SEPARATOR slot_definition SEPARATOR OBJ_END')
def expression_empty_object(p):
    while isinstance(p[0], Token) and p[0].name in {"OBJ_START", "SEPARATOR"}:
        p.pop(0)

    return Object(slots=p[0])



# @pg.production('expression : SEPARATOR SEPARATOR')
# @pg.production('expression : OBJ_START SEPARATOR')
# @pg.production('expression : BLOCK_START SEPARATOR')
# def expression_empty_slots(p):
#     return {}


# @pg.production('expression : SEPARATOR SEPARATOR')
# def expression_slots(p):
#     return {}


# def parse_slots


# @pg.production('expression : OBJ_START SEPARATOR expression SEPARATOR OBJ_END')
# def expression_object_with_slots(p):
#     return Object(slots=p[2])


parser = pg.build()

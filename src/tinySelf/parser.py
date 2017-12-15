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
from ast_tokens import Cascade
from ast_tokens import Message
from ast_tokens import KeywordMessage
from ast_tokens import BinaryMessage
from ast_tokens import Send
from ast_tokens import Self


pg = ParserGenerator(
    (
        "NUMBER",
        "OBJ_START", "OBJ_END",
        "BLOCK_START", "BLOCK_END",
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
        "ASSIGNMENT",
        "COMMENT",
    ),
    precedence=(
        ("left", ["IDENTIFIER"]),
        ("left", ["OPERATOR"]),
        ("right", ["FIRST_KW", "KEYWORD"]),
    )
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
def unary_message(p):
    return Send(obj=Self(), msg=Message(p[0].getstr()))


@pg.production('expression : expression IDENTIFIER')
def unary_message_to_expression(p):
    return Send(obj=p[0], msg=Message(p[1].getstr()))


# Binary messages #############################################################
@pg.production('expression : expression OPERATOR expression')
@pg.production('expression : expression ASSIGNMENT expression')
def binary_message_to_expression(p):
    assert len(p) == 3, "Bad number of operands for %s!" % p[1]

    return Send(p[0], BinaryMessage(p[1].getstr(), p[2]))


# Keyword messages ############################################################
@pg.production('expression : FIRST_KW expression')
def keyword_message(p):
    return Send(obj=Self(), msg=KeywordMessage(p[0].getstr(), [p[1]]))


@pg.production('expression : expression FIRST_KW expression')
def keyword_message_to_obj(p):
    return Send(obj=p[0], msg=KeywordMessage(p[1].getstr(), [p[2]]))


@pg.production('kwd : KEYWORD expression')
def keyword(p):
    return p


@pg.production('kwd : KEYWORD expression kwd')
def keyword_multiple(p):
    # flatten the nested lists
    tokens = [p[0], p[1]]
    for group in p[2:]:
        tokens.extend(group)

    return tokens


@pg.production('keyword_msg : FIRST_KW expression kwd')
def keyword_message_with_parameters(p):
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


@pg.production('keyword_msg : expression FIRST_KW expression kwd')
def keyword_message_to_obj_with_parameters(p):
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


# TODO: remove later?
@pg.production('expression : keyword_msg')
def expression_keyword_msg(p):
    return p[0]


# Cascades ####################################################################
def parse_cascade_messages(msgs):
    out = []
    for msg in msgs:
        if hasattr(msg, "obj") and msg.obj == Self():
            if isinstance(msg, Send):
                msg = msg.msg

            if isinstance(msg, Cascade):
                out.extend(msg.msgs)
                continue

        out.append(msg)

    return out


@pg.production('cascade : expression CASCADE expression')
def cascade(p):
    return Cascade(obj=Self(), msgs=parse_cascade_messages([p[0], p[2]]))


@pg.production('cascade : expression expression CASCADE expression')
def cascades(p):
    msgs = parse_cascade_messages([p[1], p[3]])

    return Cascade(obj=p[0], msgs=msgs)


# TODO: remove later?
@pg.production('expression : cascade')
def expression_cascade(p):
    return p[0]


# Slot definition #############################################################
@pg.production('slot_name : IDENTIFIER')
def slot_names(p):
    return p[0].value


@pg.production('slot_definition : slot_name')
def nil_slot_definition(p):
    return {p[0]: None}


@pg.production('slot_definition : slot_name ASSIGNMENT expression')
@pg.production('slot_definition : slot_name RW_ASSIGNMENT expression')
def slot_definition(p):
    return {p[0]: p[2]}


# Arguments
@pg.production('slot_definition : ARGUMENT')
def nil_argument_definition(p):
    return {p[0].value: None}


# Keywords
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


@pg.production('kw_slot_name : FIRST_KW IDENTIFIER')
def slot_name_kwd(p):
    """
    Returns (slotname, parameter_list)
    """
    return p[0].value, [p[1].value]


@pg.production('kw_slot_name : FIRST_KW IDENTIFIER slot_kwd')
def slot_names_kwds(p):
    """
    Returns (slotname, parameter_list)
    """
    signature = [p[0]]
    parameters = [p[1]]

    for cnt, token in enumerate(p[2]):
        if cnt % 2 == 0:
            signature.append(token)
        else:
            parameters.append(token)

    return "".join(x.value for x in signature), {x.value for x in parameters}


@pg.production('slot_definition : kw_slot_name ASSIGNMENT expression')
def kw_slot_definition(p):
    assert isinstance(p[2], Object), "Only objects are assignable to kw slots!"

    slot_name = p[0][0]
    parameters = p[0][1]

    obj = p[2]
    obj.params.extend(parameters)

    return {slot_name: obj}


# Operators
@pg.production('op_slot_name : OPERATOR IDENTIFIER')
@pg.production('op_slot_name : ASSIGNMENT IDENTIFIER')
def slot_name_op(p):
    """
    Returns (slotname, parameter_list)
    """
    return p[0].value, [p[1].value]


@pg.production('slot_definition : op_slot_name ASSIGNMENT expression')
def operator_slot_definition(p):
    assert isinstance(p[2], Object), "Only objects are assignable to op slots!"

    slot_name = p[0][0]
    parameters = p[0][1]

    obj = p[2]
    obj.params.extend(parameters)

    return {slot_name: obj}


# Allow list of dot-separated of slot definitions.
@pg.production('slot_definition : slot_definition END_OF_EXPR')
@pg.production('slot_definition : slot_definition END_OF_EXPR slot_definition')
def slots_definition(p):
    out = p[0]

    if len(p) >= 3:
        out.update(p[2])

    return out


# Object definition ###########################################################
@pg.production('obj : OBJ_START OBJ_END')
@pg.production('obj : OBJ_START SEPARATOR OBJ_END')
@pg.production('obj : OBJ_START SEPARATOR SEPARATOR OBJ_END')
def empty_object(p):
    return Object()


def parse_slots_and_params(slots):
    slot_names = []
    param_names = []
    for name in slots.keys():
        if name.startswith(":"):
            param_names.append(name)
        else:
            slot_names.append(name)

    params = [k[1:] for k in param_names]
    slots = {k: slots[k] for k in slot_names}

    return slots, params


@pg.production('obj : OBJ_START slot_definition SEPARATOR OBJ_END')
@pg.production('obj : OBJ_START SEPARATOR slot_definition SEPARATOR OBJ_END')
def object_with_slots(p):
    # remove tokens from the beginning
    while isinstance(p[0], Token) and p[0].name in {"OBJ_START", "SEPARATOR"}:
        p.pop(0)

    slots, params = parse_slots_and_params(p[0])

    return Object(slots=slots, params=params)


# Object with code
@pg.production('code : expression')
def code_definition(p):
    return p


@pg.production('code : expression END_OF_EXPR')
@pg.production('code : expression END_OF_EXPR code')
def code_definitions(p):
    out = [p[0]]

    if len(p) > 2:
        out.extend(p[2])

    return out


@pg.production('obj : OBJ_START slot_definition SEPARATOR code OBJ_END')
@pg.production('obj : OBJ_START SEPARATOR slot_definition SEPARATOR code OBJ_END')
def object_with_slots_and_code(p):
    # remove tokens from the beginning
    while isinstance(p[0], Token) and p[0].name in {"OBJ_START", "SEPARATOR"}:
        p.pop(0)

    slots, params = parse_slots_and_params(p[0])

    return Object(slots=slots, params=params, code=p[2])


# TODO: remove later?
@pg.production('expression : obj')
def expression_object(p):
    return p[0]


# Block definition ############################################################
@pg.production('block : BLOCK_START BLOCK_END')
@pg.production('block : BLOCK_START SEPARATOR BLOCK_END')
@pg.production('block : BLOCK_START SEPARATOR SEPARATOR BLOCK_END')
def empty_block(p):
    return Block()


@pg.production('block : BLOCK_START slot_definition SEPARATOR BLOCK_END')
@pg.production('block : BLOCK_START SEPARATOR slot_definition SEPARATOR BLOCK_END')
def block_with_slots(p):
    # remove tokens from the beginning
    while isinstance(p[0], Token) and p[0].name in {"BLOCK_START", "SEPARATOR"}:
        p.pop(0)

    slots, params = parse_slots_and_params(p[0])

    return Block(slots=slots, params=params)


@pg.production('block : BLOCK_START slot_definition SEPARATOR code BLOCK_END')
@pg.production('block : BLOCK_START SEPARATOR slot_definition SEPARATOR code BLOCK_END')
def block_with_slots_and_code(p):
    # remove tokens from the beginning
    while isinstance(p[0], Token) and p[0].name in {"BLOCK_START", "SEPARATOR"}:
        p.pop(0)

    slots, params = parse_slots_and_params(p[0])

    return Block(slots=slots, params=params, code=p[2])


# TODO: remove later?
@pg.production('expression : block')
def expression_block(p):
    return p[0]


parser = pg.build()

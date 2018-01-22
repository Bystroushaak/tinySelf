#! /usr/bin/env pypy
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from rply import ParserGenerator
from rply.token import Token

from lexer import lexer

from ast_tokens import Object
from ast_tokens import Block

from ast_tokens import Number
from ast_tokens import String

from ast_tokens import Message
from ast_tokens import KeywordMessage
from ast_tokens import BinaryMessage

from ast_tokens import Send
from ast_tokens import Cascade

from ast_tokens import Self
from ast_tokens import Return
from ast_tokens import AssignmentPrimitive


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
        "SELF",
    ),
    precedence=(
        ("right", ["IDENTIFIER"]),
        ("right", ["FIRST_KW", "KEYWORD"]),
        ("right", ["OPERATOR"]),
    )
)



# Multiple statements make code ###############################################
@pg.production('root : expression')
def at_the_top_of_the_root_is_just_expression(p):
    return [p[0]]


@pg.production('root : expression END_OF_EXPR')
@pg.production('root : expression END_OF_EXPR root')
def multiple_expressions_make_code(p):
    out = [p[0]]

    if len(p) > 2:
        out.extend(p[2])

    return out


# Self keyword ################################################################
@pg.production('expression : SELF')
def self_parser(p):
    return Self()


# Number ######################################################################
@pg.production('numbers : NUMBER')
def expression_number(p):
    return Number(int(p[0].getstr()))


# Strings #####################################################################
@pg.production('strings : SINGLE_Q_STRING')
@pg.production('strings : DOUBLE_Q_STRING')
def expression_string(p):
    return String(p[0].getstr()[1:-1])


# TODO: remove later?
@pg.production('expression : strings')
@pg.production('expression : numbers')
def expression_strings_numbers(p):
    return p[0]


# Unary messages ##############################################################
@pg.production('unary_message : IDENTIFIER')
def unary_message(p):
    return Send(obj=Self(), msg=Message(p[0].getstr()))


@pg.production('unary_message : expression IDENTIFIER')
def unary_message_to_expression(p):
    return Send(obj=p[0], msg=Message(p[1].getstr()))


# Binary messages #############################################################
@pg.production('binary_message : expression OPERATOR expression')
@pg.production('binary_message : expression ASSIGNMENT expression')
def binary_message_to_expression(p):
    assert len(p) == 3, "Bad number of operands for %s!" % p[1]

    return Send(p[0], BinaryMessage(p[1].getstr(), p[2]))


# Keyword messages ############################################################
@pg.production('keyword_msg : FIRST_KW expression')
def keyword_message(p):
    return Send(obj=Self(), msg=KeywordMessage(p[0].getstr(), [p[1]]))


@pg.production('keyword_msg : expression FIRST_KW expression')
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


@pg.production('keyword_msg : FIRST_KW expression kwd')
def keyword_message_to_self_with_parameters(p):
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


@pg.production('message : unary_message')
@pg.production('message : binary_message')
@pg.production('message : keyword_msg')
def all_kinds_of_messages_are_message(p):
    return p[0]

@pg.production('expression : message')
def expression_is_message(p):
    return p[0]


# Cascades ####################################################################
def parse_cascade_messages(msgs):
    out = []
    for msg in msgs:
        if hasattr(msg, "obj") and msg.obj == Self():
            if isinstance(msg, Cascade):
                out.extend(msg.msgs)
                continue

            if isinstance(msg, Send):
                msg = msg.msg

        out.append(msg)

    return out


@pg.production('cascade : message CASCADE message')
def cascade(p):
    f = p[0]
    s = p[2]

    if isinstance(f, Send):
        return Cascade(
            obj=f.obj,
            msgs=parse_cascade_messages([f.msg, s])
        )

    return Cascade(obj=Self(), msgs=parse_cascade_messages([f, s]))


@pg.production('cascade : message CASCADE cascade')
def cascades(p):
    if isinstance(p[0], Send):
        return Cascade(
            obj=p[0].obj,
            msgs=[p[0].msg] + p[2].msgs
        )

    return Cascade(obj=p[0], msgs=p[2].msgs)


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
def slot_definition(p):
    return {p[0]: p[2]}


def _to_assignment_name(name):
    return name + ":"


def _rw_slot(name, value):
    r_slot_name = name
    w_slot_name = _to_assignment_name(name)

    return {
        r_slot_name: value,
        w_slot_name: AssignmentPrimitive(),
    }


@pg.production('slot_definition : slot_name RW_ASSIGNMENT expression')
def slot_definition_rw(p):
    return _rw_slot(name=p[0], value=p[2])


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


def parse_slots_params_parents(slots):
    """
    Iterate thru a list of slots and sort them to `slots` (dict), `parameters`
    (list) and `parents` (dict).
    """
    slot_names = []
    param_names = []
    parent_names = []
    for name in slots.keys():
        if name.startswith(":"):
            param_names.append(name)
        elif name.endswith("*"):
            parent_names.append(name)
        else:
            slot_names.append(name)

    params = [k[1:] for k in param_names]  # strip : from the beginning
    parents = {k[:-1]: slots[k] for k in parent_names}  # strip * from the end
    slots = {k: slots[k] for k in slot_names}

    return slots, params, parents


def remove_obj_tokens_from_beginning(p):
    while isinstance(p[0], Token) and p[0].name == "OBJ_START":
        p.pop(0)

    while isinstance(p[0], Token) and p[0].name == "SEPARATOR":
        p.pop(0)

    return p


# @pg.production('obj : OBJ_START SEPARATOR code OBJ_END')  # doesn't work - why?
@pg.production('obj : OBJ_START SEPARATOR SEPARATOR code OBJ_END')
def object_with_just_code(p):
    p = remove_obj_tokens_from_beginning(p)

    return Object(code=p[0])


@pg.production('obj : OBJ_START slot_definition SEPARATOR OBJ_END')
@pg.production('obj : OBJ_START SEPARATOR slot_definition SEPARATOR OBJ_END')
def object_with_slots(p):
    p = remove_obj_tokens_from_beginning(p)

    slots, params, parents = parse_slots_params_parents(p[0])

    return Object(slots=slots, params=params, parents=parents)


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
    p = remove_obj_tokens_from_beginning(p)

    slots, params, parents = parse_slots_params_parents(p[0])

    return Object(slots=slots, params=params, code=p[2], parents=parents)


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


@pg.production('block : BLOCK_START code BLOCK_END')
def object_with_empty_slots_and_code(p):
    return Block(code=p[1])


# @pg.production('obj : BLOCK_START SEPARATOR code BLOCK_END')  # doesn't work - why?
@pg.production('block : BLOCK_START SEPARATOR SEPARATOR code BLOCK_END')
def object_with_empty_slots_and_code(p):
    p = remove_block_tokens_from_beginning(p)

    return Block(code=p[0])


def remove_block_tokens_from_beginning(p):
    while isinstance(p[0], Token) and p[0].name == "BLOCK_START":
        p.pop(0)

    while isinstance(p[0], Token) and p[0].name == "SEPARATOR":
        p.pop(0)

    return p


@pg.production('block : BLOCK_START slot_definition SEPARATOR BLOCK_END')
@pg.production('block : BLOCK_START SEPARATOR slot_definition SEPARATOR BLOCK_END')
def block_with_slots(p):
    p = remove_block_tokens_from_beginning(p)

    slots, params, _ = parse_slots_params_parents(p[0])

    return Block(slots=slots, params=params)


@pg.production('block : BLOCK_START slot_definition SEPARATOR code BLOCK_END')
@pg.production('block : BLOCK_START SEPARATOR slot_definition SEPARATOR code BLOCK_END')
def block_with_slots_and_code(p):
    p = remove_block_tokens_from_beginning(p)

    slots, params, _ = parse_slots_params_parents(p[0])

    return Block(slots=slots, params=params, code=p[2])


# TODO: remove later?
@pg.production('expression : block')
def expression_block(p):
    return p[0]


# Returns #####################################################################
@pg.production('expression : RETURN expression')
def return_parser(p):
    return Return(p[1])


# Paren priority ##############################################################
@pg.production('expression : OBJ_START message OBJ_END')
def paren_priority(p):
    if len(p) == 2:
        return Object()

    return p[1]


# Comments ####################################################################
@pg.production('expression : COMMENT expression')
def parse_comment(p):
    return p[1]


@pg.production('expression : expression COMMENT')
def parse_comment(p):
    return p[0]


@pg.production('expression : COMMENT')
def parse_comment(p):
    return None


# Parser initialization #######################################################
parser = pg.build()


def parse_and_lex(i):
    return [
        x for x in parser.parse(lexer.lex(i))
        if x is not None
    ]

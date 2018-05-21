# -*- coding: utf-8 -*-
from collections import OrderedDict

from rply import ParserGenerator
from rply.token import Token
from rply.token import BaseBox

from lexer import lexer

from ast_tokens import Root

from ast_tokens import Object
from ast_tokens import Block

from ast_tokens import Number
from ast_tokens import String

from ast_tokens import Message
from ast_tokens import KeywordMessage
from ast_tokens import BinaryMessage

from ast_tokens import Send
from ast_tokens import Cascade

from ast_tokens import Nil
from ast_tokens import Self
from ast_tokens import Return
from ast_tokens import AssignmentPrimitive


pg = ParserGenerator(
    (
        "NUMBER",
        "OBJ_START", "OBJ_END",
        "BLOCK_START", "BLOCK_END",
        "SINGLE_Q_STRING", "DOUBLE_Q_STRING",
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


# data types used because of rPython ##########################################
class StrContainer(BaseBox):
    def __init__(self, str):
        self.str = str


class DictContainer(BaseBox):
    def __init__(self, dict):
        self.dict = dict


class OrderedDictContainer(BaseBox):
    def __init__(self, d):
        self.dict = d

    @staticmethod
    def from_kw(key, val):
        """
        You can not use default OrderedDict's constructor under rPython,
        because you can't have objects of different types in one list / tuple.
        """
        out = OrderedDict()
        out[key] = val

        return OrderedDictContainer(out)


class ListContainer(BaseBox):
    def __init__(self, list):
        self.list = list


class KwSlotContainer(BaseBox):
    def __init__(self, slot_name, parameters):
        self.slot_name = slot_name
        self.parameters = parameters


# Multiple statements make code ###############################################
@pg.production('root : expression')
def at_the_top_of_the_root_is_just_expression(p):
    return Root([p[0]])


@pg.production('root : expression END_OF_EXPR')
@pg.production('root : expression END_OF_EXPR root')
def multiple_expressions_make_code(p):
    code = Root([p[0]])

    if len(p) > 2:
        root = p[2]
        assert isinstance(root, Root)
        code.ast.extend(root.ast)

    return code


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
    full_string = p[0].getstr()  # with ""

    # [translation:ERROR] TyperError: slice stop must be proved non-negative
    end_of_string = len(full_string) - 1

    assert len(full_string) >= 2
    assert end_of_string >= 1

    return String(full_string[1:end_of_string])  # without ""


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
    if len(p) != 3:
        raise ValueError("Bad number of operands for %s!" % p[1])

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
    return ListContainer(p)


@pg.production('kwd : KEYWORD expression kwd')
def keyword_multiple(p):
    tokens = [p[0], p[1]]

    # flatten the nested lists
    kwd = p[2]
    assert isinstance(kwd, ListContainer)
    tokens.extend(kwd.list)

    return ListContainer(tokens)


@pg.production('keyword_msg : FIRST_KW expression kwd')
def keyword_message_with_parameters(p):
    signature = [p[0].getstr()]
    parameters = [p[1]]

    kwd = p[2]
    assert isinstance(kwd, ListContainer)

    for cnt, token in enumerate(kwd.list):
        if cnt % 2 == 0:
            signature.append(token.getstr())
        else:
            parameters.append(token)

    return Send(
        obj=Self(),
        msg=KeywordMessage(
            name="".join(signature),
            parameters=parameters
        )
    )


@pg.production('keyword_msg : FIRST_KW expression kwd')
def keyword_message_to_self_with_parameters(p):
    signature = [p[0].getstr()]
    parameters = [p[1]]

    kwd = p[2]
    assert isinstance(kwd, ListContainer)

    for cnt, token in enumerate(kwd.list):
        if cnt % 2 == 0:
            signature.append(token.getstr())
        else:
            parameters.append(token)

    return Send(
        obj=Self(),
        msg=KeywordMessage(
            name="".join(signature),
            parameters=parameters
        )
    )


@pg.production('keyword_msg : expression FIRST_KW expression kwd')
def keyword_message_to_obj_with_parameters(p):
    signature = [p[1].getstr()]
    parameters = [p[2]]

    kwd = p[3]
    assert isinstance(kwd, ListContainer)

    for cnt, token in enumerate(kwd.list):
        if cnt % 2 == 0:
            signature.append(token.getstr())
        else:
            parameters.append(token)

    return Send(
        obj=p[0],
        msg=KeywordMessage(
            name="".join(signature),
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


# # Cascades ####################################################################
def parse_cascade_messages(msgs):
    out = []
    for msg in msgs:
        if (isinstance(msg, Cascade) or isinstance(msg, Send)):
            if isinstance(msg, Cascade) and msg.obj == Self():
                out.extend(msg.msgs)
                continue

            if isinstance(msg, Send) and msg.obj == Self():
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
    first = p[0]
    cascade = p[2]
    assert isinstance(cascade, Cascade)

    if isinstance(first, Send):
        assert isinstance(first, Send)
        msgs = [first.msg] + cascade.msgs

        return Cascade(obj=first.obj, msgs=msgs)

    return Cascade(obj=first, msgs=cascade.msgs)


# TODO: remove later?
@pg.production('expression : cascade')
def expression_cascade(p):
    return p[0]


# # Slot definition #############################################################
def _value_from_token(token):
    # rpython ballast
    assert isinstance(token, Token)
    assert token is not None

    value = token.value

    assert value is not None
    assert isinstance(value, str)

    return value


@pg.production('slot_name : IDENTIFIER')
def slot_names(p):
    return StrContainer(_value_from_token(p[0]))


def _str_from_strcontainer(str_container_obj):
    assert str_container_obj is not None
    assert isinstance(str_container_obj, StrContainer)

    string = str_container_obj.str
    assert string is not None
    assert isinstance(string, str)

    return string


@pg.production('slot_definition : slot_name')
def nil_slot_definition(p):
    slot_name = _str_from_strcontainer(p[0])

    return OrderedDictContainer.from_kw(slot_name, Nil())


@pg.production('slot_definition : slot_name ASSIGNMENT expression')
def slot_definition(p):
    slot_name = _str_from_strcontainer(p[0])

    return OrderedDictContainer.from_kw(slot_name, p[2])


def _to_assignment_name(name):
    assert isinstance(name, str)

    return name + ":"


def _rw_slot(name, value):
    r_slot_name = name
    w_slot_name = _to_assignment_name(name)

    out = OrderedDict()
    out[r_slot_name] = value
    out[w_slot_name] = AssignmentPrimitive()

    return out


@pg.production('slot_definition : slot_name RW_ASSIGNMENT expression')
def slot_definition_rw(p):
    slot_name = _str_from_strcontainer(p[0])

    return OrderedDictContainer(_rw_slot(name=slot_name, value=p[2]))


# Arguments
@pg.production('slot_definition : ARGUMENT')
def nil_argument_definition(p):
    slot_name = _value_from_token(p[0])

    return OrderedDictContainer.from_kw(slot_name, Nil())


# Keywords
@pg.production('slot_kwd : KEYWORD IDENTIFIER')
def slot_name_kwd_one(p):
    return ListContainer(p)


@pg.production('slot_kwd : KEYWORD IDENTIFIER slot_kwd')
def slot_name_kwd_multiple(p):
    # flatten the nested lists
    tokens = [p[0], p[1]]

    slot_kwd = p[2]
    assert isinstance(slot_kwd, ListContainer)
    tokens.extend(slot_kwd.list)

    return ListContainer(tokens)


@pg.production('kw_slot_name : FIRST_KW IDENTIFIER')
def slot_name_kwd(p):
    """
    Args:
        p[0] (Token): Slot name.
        p[1] (Token): Parameter.

    Returns:
        KwSlotContainer
    """
    return KwSlotContainer(
        slot_name=_value_from_token(p[0]),
        parameters=[_value_from_token(p[1])]
    )


@pg.production('kw_slot_name : FIRST_KW IDENTIFIER slot_kwd')
def slot_names_kwds(p):
    """
    Args:
        p[0] (Token): Slot name.
        p[1] (Token): Parameter.
        p[2:] (list): List of ListContainers with tokens.

    Returns:
        KwSlotContainer
    """
    signature = [_value_from_token(p[0])]
    parameters = [_value_from_token(p[1])]

    # unpack list of ListContainers to one list
    tokens_in_list_containers = p[2]
    assert isinstance(tokens_in_list_containers, ListContainer)

    for cnt, token in enumerate(tokens_in_list_containers.list):
        if cnt % 2 == 0:
            signature.append(_value_from_token(token))
        else:
            parameters.append(_value_from_token(token))

    return KwSlotContainer(
        slot_name="".join(signature),
        parameters=parameters
    )


@pg.production('slot_definition : kw_slot_name ASSIGNMENT expression')
def kw_slot_definition(p):
    slot_info = p[0]
    obj = p[2]

    assert isinstance(slot_info, KwSlotContainer)
    assert isinstance(obj, Object)

    obj.params.extend(slot_info.parameters)

    return OrderedDictContainer.from_kw(slot_info.slot_name, obj)


# Operators
@pg.production('op_slot_name : OPERATOR IDENTIFIER')
@pg.production('op_slot_name : ASSIGNMENT IDENTIFIER')
def slot_name_op(p):
    """
    Returns (slotname, parameter_list)
    """
    return KwSlotContainer(
        slot_name=_value_from_token(p[0]),
        parameters=[_value_from_token(p[1])]
    )


@pg.production('slot_definition : op_slot_name ASSIGNMENT expression')
def operator_slot_definition(p):
    slot_info = p[0]
    obj = p[2]

    assert isinstance(slot_info, KwSlotContainer)
    assert isinstance(obj, Object)

    obj.params.extend(slot_info.parameters)

    return OrderedDictContainer.from_kw(slot_info.slot_name, obj)


# Allow list of dot-separated of slot definitions.
@pg.production('slot_definition : slot_definition END_OF_EXPR')
@pg.production('slot_definition : slot_definition END_OF_EXPR slot_definition')
def slots_definition(p):
    out = p[0]
    assert isinstance(out, OrderedDictContainer)

    if len(p) >= 3:
        other_definitions = p[2]
        assert isinstance(other_definitions, OrderedDictContainer)

        out.dict.update(other_definitions.dict)

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
    def strip_colon_from_start(item):
        return item[1:]

    def strip_star_from_end(item):
        return item[:-1]

    params = []
    parents = {}
    only_slots = {}
    for name, value in slots.items():
        if name.startswith(":"):
            params.append(strip_colon_from_start(name))
        elif name.endswith("*"):
            parents[strip_star_from_end(name)] = value
        else:
            only_slots[name] = value

    return only_slots, params, parents


def remove_tokens_from_beginning(token_list, token_names):
    def is_token_and_has_name(item, name):
        if not isinstance(item, Token):
            return False

        assert isinstance(item, Token)  # for rPython
        return item.name == name

    for token_name in token_names:
        while is_token_and_has_name(token_list[0], token_name):
            token_list.pop(0)

    return token_list


def remove_obj_tokens_from_beginning(token_list):
    return remove_tokens_from_beginning(token_list, ["OBJ_START", "SEPARATOR"])


# @pg.production('obj : OBJ_START SEPARATOR code OBJ_END')  # doesn't work - why?
@pg.production('obj : OBJ_START SEPARATOR SEPARATOR code OBJ_END')
def object_with_just_code(p):
    p = remove_obj_tokens_from_beginning(p)

    code_container = p[0]
    assert isinstance(code_container, ListContainer)

    return Object(code=code_container.list)


@pg.production('obj : OBJ_START slot_definition SEPARATOR OBJ_END')
@pg.production('obj : OBJ_START SEPARATOR slot_definition SEPARATOR OBJ_END')
def object_with_slots(p):
    p = remove_obj_tokens_from_beginning(p)

    slot_dict = p[0]
    assert isinstance(slot_dict, OrderedDictContainer)

    slots, params, parents = parse_slots_params_parents(slot_dict.dict)

    return Object(slots=slots, params=params, parents=parents)


# Object with code
@pg.production('code : expression')
def code_definition(p):
    return ListContainer(p)


@pg.production('code : expression END_OF_EXPR')
@pg.production('code : expression END_OF_EXPR code')
def code_definitions(p):
    out = [p[0]]

    if len(p) > 2:
        code = p[2]
        assert isinstance(code, ListContainer)

        out.extend(code.list)

    return ListContainer(out)


@pg.production('obj : OBJ_START slot_definition SEPARATOR code OBJ_END')
@pg.production('obj : OBJ_START SEPARATOR slot_definition SEPARATOR code OBJ_END')
def object_with_slots_and_code(p):
    p = remove_obj_tokens_from_beginning(p)

    slot_dict = p[0]
    assert isinstance(slot_dict, OrderedDictContainer)
    slots, params, parents = parse_slots_params_parents(slot_dict.dict)

    code_container = p[2]
    assert isinstance(code_container, ListContainer)

    return Object(
        slots=slots,
        params=params,
        code=code_container.list,
        parents=parents
    )


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
    code_container = p[1]
    assert isinstance(code_container, ListContainer)  # rpython type hint

    return Block(code=code_container.list)


def remove_block_tokens_from_beginning(token_list):
    return remove_tokens_from_beginning(token_list, ["BLOCK_START", "SEPARATOR"])


# @pg.production('obj : BLOCK_START SEPARATOR code BLOCK_END')  # doesn't work - why?
@pg.production('block : BLOCK_START SEPARATOR SEPARATOR code BLOCK_END')
def object_with_empty_slots_and_code(p):
    p = remove_block_tokens_from_beginning(p)

    code_container = p[0]
    assert isinstance(code_container, ListContainer)

    return Block(code=code_container.list)


@pg.production('block : BLOCK_START slot_definition SEPARATOR BLOCK_END')
@pg.production('block : BLOCK_START SEPARATOR slot_definition SEPARATOR BLOCK_END')
def block_with_slots(p):
    p = remove_block_tokens_from_beginning(p)

    slot_dict = p[0]
    assert isinstance(slot_dict, OrderedDictContainer)

    slots, params, _ = parse_slots_params_parents(slot_dict.dict)

    return Block(slots=slots, params=params)


@pg.production('block : BLOCK_START slot_definition SEPARATOR code BLOCK_END')
@pg.production('block : BLOCK_START SEPARATOR slot_definition SEPARATOR code BLOCK_END')
def block_with_slots_and_code(p):
    p = remove_block_tokens_from_beginning(p)

    slot_dict = p[0]
    assert isinstance(slot_dict, OrderedDictContainer)
    slots, params, _ = parse_slots_params_parents(slot_dict.dict)

    code_container = p[2]
    assert isinstance(code_container, ListContainer)

    return Block(slots=slots, params=params, code=code_container.list)


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


class RemoveThis(BaseBox):
    pass


@pg.production('expression : COMMENT')
def parse_comment(p):
    return RemoveThis()


# Parser initialization #######################################################
parser = pg.build()


def lex_and_parse(i):
    tree = parser.parse(lexer.lex(i))
    assert isinstance(tree, Root)

    return [
        x for x in tree.ast
        if not isinstance(x, RemoveThis)
    ]

#! /usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
from tinySelf.lexer import lexer
from tinySelf.parser import parser

from tinySelf.ast_tokens import Send
from tinySelf.ast_tokens import Number
from tinySelf.ast_tokens import Self
from tinySelf.ast_tokens import String
from tinySelf.ast_tokens import Object
from tinySelf.ast_tokens import Message
from tinySelf.ast_tokens import BinaryMessage
from tinySelf.ast_tokens import KeywordMessage


def parse_and_lex(i):
    return parser.parse(lexer.lex(i))


def test_parse_number():
    result = parse_and_lex('1')

    assert isinstance(result, Number)
    assert result.value == 1


def test_self():
    assert Self() == Self()


def test_parse_send():
    result = parse_and_lex('asd')

    assert isinstance(result, Send)
    assert isinstance(result.obj, Self)
    assert isinstance(result.msg, Message)

    assert result.obj == Self()
    assert result.msg.name == "asd"


def test_parse_send_to_object():
    result = parse_and_lex('a b')

    assert isinstance(result, Send)
    assert isinstance(result.obj, Send)
    assert isinstance(result.msg, Message)
    assert isinstance(result.msg, Message)
    assert isinstance(result.obj.obj, Self)

    assert result.obj.obj == Self()
    assert result.obj.msg.name == "a"
    assert result.msg.name == "b"


def test_parse_binary_message():
    result = parse_and_lex('1 + 1')

    assert isinstance(result, Send)
    assert isinstance(result.obj, Number)
    assert isinstance(result.msg, BinaryMessage)
    assert isinstance(result.msg.parameter, Number)

    assert result.obj.value == 1
    assert result.msg.name == "+"
    assert result.msg.parameter.value == 1


def test_parse_keyword_message():
    result = parse_and_lex('set: 1')

    assert isinstance(result, Send)
    assert isinstance(result.obj, Self)
    assert isinstance(result.msg, KeywordMessage)
    assert isinstance(result.msg.parameters, list)

    assert result.obj == Self()
    assert result.msg.name == "set:"
    assert result.msg.parameters[0].value == 1


def test_parse_keyword_message_with_parameters():
    result = parse_and_lex('set: 1 And: 2 Also: 3 So: 4')

    assert isinstance(result, Send)
    assert isinstance(result.obj, Self)
    assert isinstance(result.msg, KeywordMessage)
    assert isinstance(result.msg.parameters, list)

    assert result.obj == Self()
    assert result.msg.name == "set:And:Also:So:"
    assert result.msg.parameters[0].value == 1
    assert result.msg.parameters[1].value == 2
    assert result.msg.parameters[2].value == 3
    assert result.msg.parameters[3].value == 4


def test_parse_keyword_message_to_obj_with_parameters():
    result = parse_and_lex('asd set: 1')

    assert isinstance(result, Send)
    assert isinstance(result.obj, Send)
    assert isinstance(result.obj.obj, Self)
    assert isinstance(result.msg, KeywordMessage)

    assert result.obj.obj == Self()
    assert result.obj.msg.name == "asd"
    assert result.msg.name == "set:"
    assert result.msg.parameters[0].value == 1


def test_parse_keyword_message_to_obj_with_parameters():
    result = parse_and_lex('asd set: 1')

    assert isinstance(result, Send)
    assert isinstance(result.obj, Send)
    assert isinstance(result.obj.obj, Self)
    assert isinstance(result.msg, KeywordMessage)

    assert result.obj.obj == Self()
    assert result.obj.msg.name == "asd"
    assert result.msg.name == "set:"
    assert result.msg.parameters[0].value == 1


def test_parse_keyword_message_to_obj_with_multiple_parameters():
    result = parse_and_lex('asd set: 1 And: 2 Also: 3 So: 4')

    assert isinstance(result, Send)
    assert isinstance(result.obj, Send)
    assert isinstance(result.obj.obj, Self)
    assert isinstance(result.msg, KeywordMessage)
    assert isinstance(result.msg.parameters, list)

    assert result.obj.obj == Self()
    assert result.obj.msg.name == "asd"
    assert result.msg.name == "set:And:Also:So:"
    assert result.msg.parameters[0].value == 1
    assert result.msg.parameters[1].value == 2
    assert result.msg.parameters[2].value == 3
    assert result.msg.parameters[3].value == 4


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


def test_parse_object_with_empty_slots():
    result = parse_and_lex('(||)')

    assert isinstance(result, Object)
    assert result.slots == {}
    assert result.code == []


def test_parse_object_with_nil_slot():
    result = parse_and_lex('(| asd |)')
    assert result == Object(slots={"asd": None})

    result = parse_and_lex('(| asd. |)')
    assert result == Object(slots={"asd": None})

    result = parse_and_lex('(asd |)')
    assert result == Object(slots={"asd": None})

    result = parse_and_lex('( asd. |)')
    assert result == Object(slots={"asd": None})


def test_parse_object_with_multiple_nil_slots():
    result = parse_and_lex('(| asd. bsd |)')
    assert result == Object(slots={"asd": None, "bsd": None})

    result = parse_and_lex('(| asd. bsd. |)')
    assert result == Object(slots={"asd": None, "bsd": None})

    result = parse_and_lex('(asd. bsd. |)')
    assert result == Object(slots={"asd": None, "bsd": None})


def test_parse_slot_assignment():
    result = parse_and_lex('(| asd <- 2 |)')
    assert result == Object(slots={"asd": Number(2)})

    result = parse_and_lex('(| asd <- 2. |)')
    assert result == Object(slots={"asd": Number(2)})


def test_parse_multiple_slot_assignment():
    result = parse_and_lex('(asd <- 2. bsd <- 4 |)')
    assert result == Object(slots={"asd": Number(2), "bsd": Number(4)})

    result = parse_and_lex('(| asd <- 2. bsd <- 4. |)')
    assert result == Object(slots={"asd": Number(2), "bsd": Number(4)})


def test_parse_kwd_slot_assignment():
    result = parse_and_lex('(| asd: a <- () |)')
    assert result == Object(slots={"asd:": Object(params=["a"])})

    result = parse_and_lex('(| asd: a <- (). |)')
    assert result == Object(slots={"asd:": Object(params=["a"])})


def test_parse_kwd_slots_assignment():
    result = parse_and_lex('(| asd: a Bsd: b <- () |)')
    assert result == Object(slots={"asd:Bsd:": Object(params=["a", "b"])})

    result = parse_and_lex('(asd: a Bsd: b <- (). |)')
    assert result == Object(slots={"asd:Bsd:": Object(params=["a", "b"])})


def test_parse_multiple_slots_assignments():
    result = parse_and_lex('(| asd: a Bsd: b <- (). a: p <- () |)')

    assert result == Object(
        slots={
            "asd:Bsd:": Object(params=["a", "b"]),
            "a:": Object(params=["p"]),
        }
    )


def test_parse_error_in_msg_slot_value_assignment():
    try:
        parse_and_lex('(| asd: a Bsd: b <- 1 |)')
    except AssertionError:
        return

    raise AssertionError("KW slot value assignment shouldn't be allowed!")


def test_parse_op_slot_assignment():
    result = parse_and_lex('(| + b <- () |)')
    assert result == Object(slots={"+": Object(params=["b"])})

    result = parse_and_lex('(+ b <- (). |)')
    assert result == Object(slots={"+": Object(params=["b"])})


def test_parse_multiple_op_slot_assignments():
    result = parse_and_lex('(| + b <- (). - a <- () |)')
    assert result == Object(
        slots={
            "+": Object(params=["b"]),
            "-": Object(params=["a"]),
        }
    )


def test_parse_slot_definition_with_combination_of_slots():
    result = parse_and_lex("""
        (|
            a.
            asd: b <- ().
            asd: a Bsd: b <- ().
            + b <- ().
            - a <- ().
        |)
    """)
    assert result == Object(
        slots={
            "a": None,
            "asd:Bsd:": Object(params=["a", "b"]),
            "asd:": Object(params=["b"]),
            "+": Object(params=["b"]),
            "-": Object(params=["a"]),
        }
    )


def test_argument_parser():
    result = parse_and_lex('(| :a |)')
    assert result == Object(params=["a"])

    result = parse_and_lex('(| :a. |)')
    assert result == Object(params=["a"])

    result = parse_and_lex('(| :a. :b |)')
    assert result == Object(params=["a", "b"])

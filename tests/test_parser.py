# -*- coding: utf-8 -*-
import pytest
from collections import OrderedDict

import rply

from tinySelf.parser import lex_and_parse
from tinySelf.parser.parser import _rw_slot

from tinySelf.parser.ast_tokens import Nil
from tinySelf.parser.ast_tokens import Send
from tinySelf.parser.ast_tokens import Self
from tinySelf.parser.ast_tokens import Block
from tinySelf.parser.ast_tokens import Object
from tinySelf.parser.ast_tokens import IntNumber
from tinySelf.parser.ast_tokens import FloatNumber
from tinySelf.parser.ast_tokens import String
from tinySelf.parser.ast_tokens import Resend
from tinySelf.parser.ast_tokens import Return
from tinySelf.parser.ast_tokens import Cascade
from tinySelf.parser.ast_tokens import Comment
from tinySelf.parser.ast_tokens import Message
from tinySelf.parser.ast_tokens import BinaryMessage
from tinySelf.parser.ast_tokens import KeywordMessage
from tinySelf.parser.ast_tokens import AssignmentPrimitive


def join_dicts(*args):
    out = OrderedDict()
    for i in args:
        out.update(i)

    return out


def rw_slots(slot_dict):
    slots = (_rw_slot(k, v) for k, v in slot_dict.iteritems())

    out = OrderedDict()
    for i in slots:
        out.update(i)

    return out


def test_parse_int_number():
    result = lex_and_parse('1')

    assert result == [IntNumber(1)]


def test_parse_float_number():
    result = lex_and_parse('1.2')

    assert result == [FloatNumber(1.2)]


def test_parse_hex_number():
    result = lex_and_parse('0x2222')

    assert result == [IntNumber(8738)]


def test_self_eq():
    assert Self() == Self()


def test_parse_send():
    result = lex_and_parse('asd')

    assert result == [Send(
        obj=Self(),
        msg=Message('asd')
    )]


def test_parse_send_to_object():
    result = lex_and_parse('a b')

    assert result == [Send(
        obj=Send(
            obj=Self(),
            msg=Message('a')
        ),
        msg=Message('b')
    )]


def test_parse_multiple_sends():
    result = lex_and_parse('a b c d e f g')

    assert result == [Send(
        obj=Send(
            obj=Send(
                obj=Send(
                    obj=Send(
                        obj=Send(
                            obj=Send(
                                obj=Self(),
                                msg=Message('a')
                            ),
                            msg=Message('b')
                        ),
                        msg=Message('c')
                    ),
                    msg=Message('d')
                ),
                msg=Message('e')
            ),
            msg=Message('f')
        ),
        msg=Message('g')
    )]


def test_parse_binary_message():
    result = lex_and_parse('1 + 1')

    assert result == [Send(
        obj=IntNumber(1),
        msg=BinaryMessage(
            name='+',
            parameter=IntNumber(1)
        )
    )]


def test_parse_keyword_message():
    result = lex_and_parse('set: 1')

    assert result == [Send(
        obj=Self(),
        msg=KeywordMessage(
            name='set:',
            parameters=[IntNumber(1)]
        )
    )]


def test_parse_keyword_message_with_parameters():
    result = lex_and_parse('set: 1 And: 2 Also: 3 So: 4')

    assert result == [Send(
        obj=Self(),
        msg=KeywordMessage(
            name='set:And:Also:So:',
            parameters=[
                IntNumber(1),
                IntNumber(2),
                IntNumber(3),
                IntNumber(4)
            ]
        )
    )]


def test_parse_keyword_message_to_obj_with_parameters():
    result = lex_and_parse('asd set: 1')

    assert result == [Send(
        obj=Send(
            obj=Self(),
            msg=Message('asd')
        ),
        msg=KeywordMessage(
            name='set:',
            parameters=[IntNumber(1)]
        )
    )]


def test_parse_keyword_message_to_obj_with_multiple_parameters():
    result = lex_and_parse('asd set: 1 And: 2 Also: 3 So: 4')

    assert result == [Send(
        obj=Send(
            obj=Self(),
            msg=Message('asd')
        ),
        msg=KeywordMessage(
            name='set:And:Also:So:',
            parameters=[
                IntNumber(1),
                IntNumber(2),
                IntNumber(3),
                IntNumber(4)
            ]
        )
    )]


def test_parse_keyword_fails_if_first_is_not_uppercase():
    with pytest.raises(rply.ParsingError):
        lex_and_parse('asd Set: 1 And: 2')


def test_parse_string():
    result = lex_and_parse('"asd"')

    assert isinstance(result[0], String)
    assert result[0].value == "asd"

    result = lex_and_parse("'asd'")
    assert result[0].value == "asd"

    result = lex_and_parse('""')
    assert result[0].value == ""


def test_parse_chained_messages():
    result = lex_and_parse('2 minus minus')

    assert result == [Send(
        obj=Send(
            obj=IntNumber(2),
            msg=Message('minus'),
        ),
        msg=Message('minus')
    )]


def test_parse_chained_messages_kw():
    result = lex_and_parse('2 minus ifTrue: []')

    assert result == [Send(
        obj=Send(
            obj=IntNumber(2),
            msg=Message('minus')
        ),
        msg=KeywordMessage(
            name='ifTrue:',
            parameters=[
                Block()
            ]
        )
    )]


def test_parse_chained_kw_and_unary_msgs():
    result = lex_and_parse('ifTrue: [] not not')

    assert result == [
        Send(
            obj=Self(),
            msg=KeywordMessage(name='ifTrue:', parameters=[
                Send(
                    obj=Send(
                        obj=Block(),
                        msg=Message('not')
                    ),
                    msg=Message('not')
                )
            ])
        ),
    ]


def test_parse_cascade_to_self():
    result = lex_and_parse('a; b')

    assert result == [Cascade(
        obj=Self(),
        msgs=[
            Message("a"),
            Message("b"),
        ]
    )]


def test_parse_cascade_kw_to_self():
    result = lex_and_parse('a: 1; b')

    assert result == [Cascade(
        obj=Self(),
        msgs=[
            KeywordMessage("a:", [IntNumber(1)]),
            Message("b"),
        ]
    )]


def test_parse_cascade():
    result = lex_and_parse('a b; c')

    assert result == [Cascade(
        obj=Send(Self(), Message("a")),
        msgs=[
            Message("b"),
            Message("c"),
        ]
    )]


def test_parse_cascade_kw():
    result = lex_and_parse('s a: 1 B: 2; b')

    assert result == [Cascade(
        obj=Send(Self(), Message("s")),
        msgs=[
            KeywordMessage("a:B:", [IntNumber(1), IntNumber(2)]),
            Message("b"),
        ]
    )]


def test_parse_cascade_to_kw():
    result = lex_and_parse('x: 1 Y: 2; a: 1 B: 2; b')

    assert result == [Cascade(
        obj=Self(),
        msgs=[
            KeywordMessage("x:Y:", [IntNumber(1), IntNumber(2)]),
            KeywordMessage("a:B:", [IntNumber(1), IntNumber(2)]),
            Message("b"),
        ]
    )]


def test_multiple_cascades():
    result = lex_and_parse('obj a; b; c')

    assert result == [Cascade(
        obj=Send(
            Self(),
            Message("obj")
        ),
        msgs=[
            Message("a"),
            Message("b"),
            Message("c"),
        ]
    )]


# Objects #####################################################################
def test_parse_object():
    result = lex_and_parse('()')

    assert isinstance(result[0], Object)
    assert result[0].slots == {}
    assert result[0].code == []


def test_parse_object_with_spaces():
    result = lex_and_parse('(    )')

    assert isinstance(result[0], Object)
    assert result[0].slots == {}
    assert result[0].code == []


def test_parse_object_with_empty_slots():
    result = lex_and_parse('(||)')

    assert isinstance(result[0], Object)
    assert result[0].slots == {}
    assert result[0].code == []


def test_parse_object_with_nil_slot():
    result = lex_and_parse('(| asd |)')
    assert result == [Object(slots=_rw_slot("asd", Nil()))]

    result = lex_and_parse('(| asd. |)')
    assert result == [Object(slots=_rw_slot("asd", Nil()))]

    result = lex_and_parse('(asd |)')
    assert result == [Object(slots=_rw_slot("asd", Nil()))]

    result = lex_and_parse('( asd. |)')
    assert result == [Object(slots=_rw_slot("asd", Nil()))]


def test_parse_object_with_multiple_nil_slots():
    expected_result = [Object(
        slots=OrderedDict((
            ("asd", Nil()),
            ("asd:", AssignmentPrimitive()),
            ("bsd", Nil()),
            ("bsd:", AssignmentPrimitive())
        ))
    )]

    result = lex_and_parse('(| asd. bsd |)')
    assert result == expected_result

    result = lex_and_parse('(| asd. bsd. |)')
    assert result == expected_result

    result = lex_and_parse('(asd. bsd. |)')
    assert result == expected_result


def test_parse_slot_assignment():
    result = lex_and_parse('(| asd <- 2 |)')
    assert result == [Object(slots=_rw_slot("asd", IntNumber(2)))]

    result = lex_and_parse('(| asd <- 2. |)')
    assert result == [Object(slots=_rw_slot("asd", IntNumber(2)))]


def test_parse_multiple_slot_assignment():
    result = lex_and_parse('(asd <- 2. bsd <- 4 |)')
    assert result == [Object(
        slots=rw_slots(OrderedDict((
            ("asd", IntNumber(2)),
            ("bsd", IntNumber(4))
        )))
    )]

    result = lex_and_parse('(| asd <- 2. bsd <- 4. |)')
    assert result == [Object(
        slots=rw_slots(OrderedDict((
            ("asd", IntNumber(2)),
            ("bsd", IntNumber(4))
        )))
    )]


def test_parse_rw_slot_assignment():
    result = lex_and_parse('( a <- 2 |)')

    assert result == [Object(slots=_rw_slot("a", IntNumber(2)))]


def test_parse_kwd_slot_assignment():
    result = lex_and_parse('(| asd: a = () |)')
    assert result == [Object(slots={"asd:": Object(params=["a"])})]

    result = lex_and_parse('(| asd: a = (). |)')
    assert result == [Object(slots={"asd:": Object(params=["a"])})]


def test_parse_kwd_slots_assignment():
    result = lex_and_parse('(| asd: a Bsd: b = () |)')
    assert result == [Object(slots={"asd:Bsd:": Object(params=["a", "b"])})]


def test_parse_kwd_slots_assignment_without_openning_slots():
    result = lex_and_parse('(| asd: a Bsd: b = (). |)')
    assert result == [Object(slots={"asd:Bsd:": Object(params=["a", "b"])})]


def test_parse_multiple_slots_assignments():
    result = lex_and_parse('(| asd: a Bsd: b = (). a: p = () |)')

    assert result == [Object(
        slots=OrderedDict((
            ("asd:Bsd:", Object(params=["a", "b"])),
            ("a:", Object(params=["p"])),
        ))
    )]


def test_parse_error_in_msg_slot_value_assignment():
    try:
        lex_and_parse('(| asd: a Bsd: b = 1 |)')
    except AssertionError:
        return

    raise AssertionError("KW slot value assignment shouldn't be allowed!")


def test_parse_op_slot_assignment():
    result = lex_and_parse('(| + b = () |)')
    assert result == [Object(slots={"+": Object(params=["b"])})]

    result = lex_and_parse('(+ b = (). |)')
    assert result == [Object(slots={"+": Object(params=["b"])})]


def test_parse_multiple_op_slot_assignments():
    result = lex_and_parse('(| + b = (). - a = () |)')
    assert result == [Object(
        slots={
            "+": Object(params=["b"]),
            "-": Object(params=["a"]),
        }
    )]


def test_parse_slot_definition_with_combination_of_slots():
    result = lex_and_parse("""
        (|
            a.
            asd: b = ().
            asd: a Bsd: b = ().
            + b = ().
            - a = ().
            = a = ().
        |)
    """)

    slots = _rw_slot("a", Nil())
    slots.update(OrderedDict((
        ("asd:", Object(params=["b"])),
        ("asd:Bsd:", Object(params=["a", "b"])),
        ("+", Object(params=["b"])),
        ("-", Object(params=["a"])),
        ("=", Object(params=["a"])),
    )))

    assert result[0] == Object(slots=slots)


def test_argument_parser():
    result = lex_and_parse('(| :a |)')
    assert result == [Object(params=["a"])]

    result = lex_and_parse('(| :a. |)')
    assert result == [Object(params=["a"])]

    result = lex_and_parse('(| :a. :b |)')
    assert result == [Object(params=["a", "b"])]


def test_obj_with_code():
    result = lex_and_parse('(| a | a printLine)')

    assert result == [Object(
        slots=_rw_slot("a", Nil()),
        code=[
            Send(
                Send(Self(), Message("a")),
                Message("printLine")
            )
        ]
    )]


def test_obj_with_code_with_dot():
    result = lex_and_parse('(| a | a printLine.)')

    assert result == [Object(
        slots=_rw_slot("a", Nil()),
        code=[
            Send(
                Send(Self(), Message("a")),
                Message("printLine")
            )
        ]
    )]


def test_obj_with_code_statements():
    result = lex_and_parse('(| a | a printLine. a print. test)')

    assert result == [Object(
        slots=_rw_slot("a", Nil()),
        code=[
            Send(
                Send(Self(), Message("a")),
                Message("printLine")
            ),
            Send(
                Send(Self(), Message("a")),
                Message("print")
            ),
            Send(Self(), Message("test"))
        ]
    )]


def test_recursive_obj_definition():
    result = lex_and_parse("""
        (|
            a = (| var | var printLine. var).
            b <- nil.
        | nil.)
    """)

    assert result == [Object(
        slots=join_dicts(
            {
                "a": Object(
                    slots=_rw_slot("var", Nil()),
                    code=[
                        Send(
                            Send(Self(), Message("var")),
                            Message("printLine")
                        ),
                        Send(Self(), Message("var")),
                    ]
                )
            },
            _rw_slot("b", Send(Self(), Message("nil")))
        ),
        code=[Send(Self(), Message("nil"))]
    )]


def test_object_without_slots():
    result = lex_and_parse('(|| a printLine)')

    assert result == [Object(
        code=[
            Send(
                Send(Self(), Message("a")),
                Message("printLine")
            )
        ]
    )]


def test_object_with_parents():
    result = lex_and_parse('(| p* = traits | a printLine)')

    assert result == [Object(
        parents={"p": Send(Self(), Message("traits"))},
        code=[
            Send(
                Send(Self(), Message("a")),
                Message("printLine")
            )
        ]
    )]


def test_objects_with_objects_in_slots():
    result = lex_and_parse("""(|
    append: s = (||"Str: ")
|)""")

    assert result == [Object(
        slots=OrderedDict([
            ("append:", Object(params=["s"], code=[String("Str: ")])),
        ])
    )]


# TODO: update parser to support this (parens with dots / multiple expressions
#       are considered code objects, not precedence)
# def test_objects_with_objects_in_slots_defined_just_by_parans():
#     result = lex_and_parse("""(|
#     append: s = ("Str: ".)
# |)""")

#     assert result == [Object(
#         slots=OrderedDict([
#             ("append:", Object(params=["s"], code=[String("Str: ")])),
#         ])
#     )]


# Blocks ######################################################################
def test_empty_block():
    result = lex_and_parse('[]')
    assert result == [Block()]


def test_block_slots():
    # result = lex_and_parse('[ asd. |]')
    # assert result == Block(slots={"asd": None})

    result = lex_and_parse('[| asd <- 2 |]')
    assert result == [Block(slots=_rw_slot("asd", IntNumber(2)))]

    result = lex_and_parse('[| asd <- 2. |]')
    assert result == [Block(slots=_rw_slot("asd", IntNumber(2)))]

    result = lex_and_parse('[asd <- 2. bsd <- 4 |]')
    assert result == [Block(slots=rw_slots(OrderedDict(
        (
            ("asd", IntNumber(2)),
            ("bsd", IntNumber(4)))
        )
    ))]

    result = lex_and_parse('[| asd <- 2. bsd <- 4. |]')
    assert result == [Block(slots=rw_slots(OrderedDict(
        (
            ("asd", IntNumber(2)),
            ("bsd", IntNumber(4))
        )
    )))]

    result = lex_and_parse('[| asd: a = () |]')
    assert result == [Block(slots={"asd:": Object(params=["a"])})]

    result = lex_and_parse('[| asd: a = (). |]')
    assert result == [Block(slots={"asd:": Object(params=["a"])})]

    result = lex_and_parse('[| asd: a Bsd: b = () |]')
    assert result == [Block(slots={"asd:Bsd:": Object(params=["a", "b"])})]

    result = lex_and_parse('[| :a |]')
    assert result == [Block(params=["a"])]

    result = lex_and_parse('[| :a. |]')
    assert result == [Block(params=["a"])]

    result = lex_and_parse('[| :a. :b |]')
    assert result == [Block(params=["a", "b"])]

    result = lex_and_parse('[:a |]')
    assert result == [Block(params=["a"])]

    result = lex_and_parse('[ :a. |]')
    assert result == [Block(params=["a"])]

    result = lex_and_parse('[:a. :b |]')
    assert result == [Block(params=["a", "b"])]

    result = lex_and_parse('[| + b = () |]')
    assert result == [Block(slots={"+": Object(params=["b"])})]

    result = lex_and_parse('[+ b = (). |]')
    assert result == [Block(slots={"+": Object(params=["b"])})]

    result = lex_and_parse('[| + b = (). - a = () |]')
    assert result == [Block(
        slots={
            "+": Object(params=["b"]),
            "-": Object(params=["a"]),
        }
    )]


def test_block_empty_slots_and_code():
    result = lex_and_parse('[|| a printLine. a print. test]')

    assert result == [Block(
        code=[
            Send(
                Send(Self(), Message("a")),
                Message("printLine")
            ),
            Send(
                Send(Self(), Message("a")),
                Message("print")
            ),
            Send(Self(), Message("test"))
        ]
    )]


def test_block_with_code_statements():
    result = lex_and_parse('[| a. :b | a printLine. a print. test]')

    assert result == [Block(
        slots=_rw_slot("a", Nil()),
        params=["b"],
        code=[
            Send(
                Send(Self(), Message("a")),
                Message("printLine")
            ),
            Send(
                Send(Self(), Message("a")),
                Message("print")
            ),
            Send(Self(), Message("test"))
        ]
    )]


def test_block_with_just_code():
    result = lex_and_parse('[ a printLine. a print. test]')

    assert result == [Block(
        code=[
            Send(
                Send(Self(), Message("a")),
                Message("printLine")
            ),
            Send(
                Send(Self(), Message("a")),
                Message("print")
            ),
            Send(Self(), Message("test"))
        ]
    )]


# Return ######################################################################
def test_return_in_block():
    result = lex_and_parse('[ a printLine. a print. ^test]')

    assert result == [Block(
        code=[
            Send(
                Send(Self(), Message("a")),
                Message("printLine")
            ),
            Send(
                Send(Self(), Message("a")),
                Message("print")
            ),
            Return(Send(Self(), Message("test")))
        ]
    )]


def test_double_return():
    result = lex_and_parse('''
    (| dict_mirror |
        dict_mirror: primitives mirrorOn: dict.

        dict_mirror toSlot: 'at:Fail:' Add: (
            | :key. :fail_blck. block_run <- false. |

            (result is: nil) ifTrue: [ block_run: true. ^ fail_blck value].
        ).
    ).
''')

    assert result == [
        Object(
            slots=OrderedDict([
                ["dict_mirror", Nil()],
                ["dict_mirror:", AssignmentPrimitive()]
            ]),
            code=[
                Send(
                    obj=Self(),
                    msg=KeywordMessage(
                        name="dict_mirror:",
                        parameters=[
                            Send(
                                obj=Send(obj=Self(), msg=Message("primitives")),
                                msg=KeywordMessage(
                                    name="mirrorOn:",
                                    parameters=[
                                        Send(obj=Self(), msg=Message("dict"))
                                    ]
                                )
                            )
                        ]
                    )
                ),
                Send(
                    obj=Send(obj=Self(), msg=Message("dict_mirror")),
                    msg=KeywordMessage(
                        name="toSlot:Add:",
                        parameters=[
                            String('at:Fail:'),
                            Object(
                                slots=OrderedDict([
                                    ["block_run", Send(obj=Self(), msg=Message("false"))],
                                    ["block_run:", AssignmentPrimitive()]
                                ]),
                                params=["key", "fail_blck"],
                                code=[
                                    Send(
                                        obj=Send(
                                            obj=Send(
                                                obj=Self(),
                                                msg=Message("result")
                                            ),
                                            msg=KeywordMessage(
                                                name="is:",
                                                parameters=[
                                                    Send(obj=Self(), msg=Message("nil"))
                                                ]
                                            )
                                        ),
                                        msg=KeywordMessage(
                                            name="ifTrue:",
                                            parameters=[
                                                Block(
                                                    code=[
                                                        Send(
                                                            obj=Self(),
                                                            msg=KeywordMessage(
                                                                name="block_run:",
                                                                parameters=[
                                                                    Send(obj=Self(), msg=Message("true"))
                                                                ]
                                                            )
                                                        ),
                                                        Return(
                                                            Send(
                                                                obj=Send(obj=Self(), msg=Message("fail_blck")),
                                                                msg=Message("value")
                                                            )
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    )
                                ]
                            )
                        ]
                    )
                )
            ]
        )
    ]


def test_return_in_object():
    result = lex_and_parse('(|| a printLine. a print. ^test.)')

    assert result == [Object(
        code=[
            Send(
                Send(Self(), Message("a")),
                Message("printLine")
            ),
            Send(
                Send(Self(), Message("a")),
                Message("print")
            ),
            Return(Send(Self(), Message("test")))
        ]
    )]


# Self ########################################################################
def test_self_kw():
    result = lex_and_parse('(|| self)')

    assert result == [Object(
        code=[
            Self()
        ]
    )]

    result = lex_and_parse('(|| self xe)')

    assert result == [Object(
        code=[
            Send(Self(), Message("xe"))
        ]
    )]


# Parens for priority #########################################################
def test_parens_for_priority():
    result = lex_and_parse('(|| 1 > (2 xex: 1) ifTrue: [] )')

    assert result == [Object(code=[
        Send(
            obj=Send(
                obj=IntNumber(1),
                msg=BinaryMessage(
                    name='>',
                    parameter=Send(
                        obj=IntNumber(2),
                        msg=KeywordMessage(
                            name='xex:',
                            parameters=[IntNumber(1)]
                        )
                    )
                )
            ),
            msg=KeywordMessage(
                name='ifTrue:',
                parameters=[Block()]
            )
        )
    ])]

    # and now without parens
    result = lex_and_parse('(|| 1 > 2 xex: 1 ifTrue: [] )')

    assert result == [Object(code=[
        Send(
            obj=Send(
                obj=IntNumber(1),
                msg=BinaryMessage(name='>', parameter=IntNumber(2))
            ),
            msg=KeywordMessage(
                name='xex:',
                parameters=[
                    Send(
                        obj=IntNumber(1),
                        msg=KeywordMessage(
                            name='ifTrue:', parameters=[Block()]
                        )
                    )
                ]
            )
        )
    ])]


# Comments ####################################################################
def test_parse_comment():
    result = lex_and_parse('(|| self) # xe')

    assert result == [Object(code=[Self()])]


def test_parse_multiline_comment():
    result = lex_and_parse('''
    # this is example
    # of the multiline comment
        (|| self) # xe
    ''')

    assert result == [Object(code=[Self()])]


def test_parse_just_comment():
    result = lex_and_parse('# comment')

    assert result == [Comment("# comment")]


# Multiple statements are code ################################################
def test_multiple_statements_make_code():
    result = lex_and_parse('''
        xe.
        (|| self).
        1'''
    )

    assert result == [
        Send(obj=Self(), msg=Message('xe')),
        Object(code=[Self()]),
        IntNumber(1)
    ]


# Resends #####################################################################
def test_resend():
    result = lex_and_parse('''(| p* = xe. |
        p.msg.
        p.kwd: x Msg: y.
    )''')

    assert result == [
        Object(
            code=[
                Resend(parent_name="p", msg=Message("msg")),
                Resend(parent_name="p", msg=KeywordMessage(
                    name="kwd:Msg:",
                    parameters=[
                        Send(obj=Self(), msg=Message("x")),
                        Send(obj=Self(), msg=Message("y"))
                    ]
                ))
            ],
            parents={"p": Send(obj=Self(), msg=Message("xe"))})
    ]

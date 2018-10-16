# -*- coding: utf-8 -*-
from pytest import raises

from tinySelf.vm.interpreter import NIL
from tinySelf.vm.interpreter import Interpreter

from tinySelf.vm.code_context import CodeContext

from tinySelf.vm.primitives import get_primitives
from tinySelf.vm.primitives import PrimitiveIntObject

from tinySelf.parser import lex_and_parse


def test_interpreter():
    ast = lex_and_parse("""(|
        a <- 1.
        add: b = (||
            (a + 1) + b
        )
    |) add: 2""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(context, universe=get_primitives())

    result = interpreter.interpret()
    assert result == PrimitiveIntObject(4)


def test_assignment_primitive():
    ast = lex_and_parse("""(|
        a <- 0.
        incA = (||
            a: 1.
            ^a
        )
    |) incA""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(context, universe=get_primitives())

    result = interpreter.interpret()
    assert result == PrimitiveIntObject(1)


def test_block():
    ast = lex_and_parse("""(|
        a <- 0.
        addTenToBlk: blk = (||
            10 + (blk value).
        ).

        add = (| tmp = 3. tmp_block. |
            tmp_block: [a + tmp].
            a: 1.  # block should reflect current scopes
            2 + addTenToBlk: tmp_block.
        )
    |) add""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(context, universe=get_primitives())

    result = interpreter.interpret()
    assert result == PrimitiveIntObject(16)


def test_block_with_argument():
    ast = lex_and_parse("""(|
        a <- 0.
        giveOneToBlock: blk = (||
            blk with: 1
        ).

        shouldBeThree = (| tmp = 1. block. |
            block: [| :x | a + tmp + x].
            a: 1.
            giveOneToBlock: block.
        )
    |) shouldBeThree""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(context, universe=get_primitives())

    result = interpreter.interpret()
    assert result == PrimitiveIntObject(3)


def test_calling_block_twice_with_argument():
    ast = lex_and_parse("""(|
        a <- 0.
        giveOneToBlock: blk = (||
            blk with: 1
        ).

        giveTwoToBlock: blk = (||
            blk with: 2
        ).

        shouldBeThree = (| tmp = 1. block. sub_result. |
            block: [| :x | a + tmp + x].
            a: 1.
            sub_result: giveOneToBlock: block.
            ^ sub_result + giveTwoToBlock: block
        )
    |) shouldBeThree""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(context, universe=get_primitives())

    result = interpreter.interpret()
    assert result == PrimitiveIntObject(7)


def test_resend():
    ast = lex_and_parse("""(|
        p* = (| xex = 1. |).
        q* = (| xex = 2. |).

        fetchXex = (|| q.xex)
    |) fetchXex""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(context, universe=get_primitives())

    result = interpreter.interpret()
    assert result == PrimitiveIntObject(2)


def test_resend_is_in_local_context():
    ast = lex_and_parse("""(|
        p* = (| xex = (|| ^1). |).
        q* = (| xex = (|| a + 1). |).
        a = 1.

        fetchXex = (|| q.xex)
    |) fetchXex""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(context, universe=get_primitives())

    result = interpreter.interpret()
    assert result == PrimitiveIntObject(2)


def test_resend_keyword():
    ast = lex_and_parse("""(|
        p* = (| xex: a = (|| 1). |).
        q* = (| xex: a = (|| a). |).

        fetchXex = (|| q.xex: 2)
    |) fetchXex""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(context, universe=get_primitives())

    result = interpreter.interpret()
    assert result == PrimitiveIntObject(2)

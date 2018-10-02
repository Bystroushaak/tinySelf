# -*- coding: utf-8 -*-
from pytest import raises

from tinySelf.vm.interpreter import Frame
from tinySelf.vm.interpreter import NIL
from tinySelf.vm.interpreter import Interpreter

from tinySelf.vm.code_context import CodeContext

from tinySelf.vm.primitives import get_primitives
from tinySelf.vm.primitives import PrimitiveIntObject

from tinySelf.parser import lex_and_parse


def test_frame():
    f = Frame()
    f.push(PrimitiveIntObject(1))
    f.push(PrimitiveIntObject(2))

    assert f.pop() == PrimitiveIntObject(2)
    assert f.pop() == PrimitiveIntObject(1)

    with raises(IndexError):
        f.pop()

    assert f.pop_or_nil() == NIL
    f.push(PrimitiveIntObject(1))
    assert f.pop_or_nil() == PrimitiveIntObject(1)
    assert f.pop_or_nil() == NIL


def test_interpreter():
    ast = lex_and_parse("""(|
        a <- 1.
        add: b = (||
            (a + 1) + b
        )
    |) add: 2""")

    context = ast[0].compile(CodeContext())

    interpreter = Interpreter(universe=get_primitives())

    result = interpreter.interpret(context, Frame())
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
    interpreter = Interpreter(universe=get_primitives())

    result = interpreter.interpret(context, Frame())
    assert result == PrimitiveIntObject(1)


def test_block():
    ast = lex_and_parse("""(|
        a <- 0.
        addTenToBlk: blk = (||
            10 + (blk value).
        ).

        add = (| tmp = 3. tmp_block. |
            tmp_block: [a + tmp].
            a: 1.
            2 + addTenToBlk: tmp_block.
        )
    |) add""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives())

    result = interpreter.interpret(context, Frame())
    assert result == PrimitiveIntObject(16)

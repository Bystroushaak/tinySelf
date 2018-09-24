# -*- coding: utf-8 -*-
from pytest import raises

from tinySelf.vm.interpreter import Frame
from tinySelf.vm.interpreter import BOXED_NIL
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

    assert f.pop_or_nil() == BOXED_NIL
    f.push(PrimitiveIntObject(1))
    assert f.pop_or_nil() == PrimitiveIntObject(1)
    assert f.pop_or_nil() == BOXED_NIL


def test_interpreter():
    ast = lex_and_parse("""(|
        a <- 1.
        print: b = (||
            (a + 1) print
        )
    |) print: 1""")

    context = ast[0].compile(CodeContext())

    frame = Frame()
    interpreter = Interpreter(universe=get_primitives())

    interpreter.interpret(context, frame)

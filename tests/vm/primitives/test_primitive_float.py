# -*- coding: utf-8 -*-
import pytest

from tinySelf.parser import lex_and_parse
from tinySelf.vm.interpreter import Interpreter
from tinySelf.vm.code_context import CodeContext

from tinySelf.vm.primitives import get_primitives
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveFloatObject
from tinySelf.vm.primitives import PrimitiveTrueObject
from tinySelf.vm.primitives import PrimitiveFalseObject




def test_instanciation():
    obj = PrimitiveFloatObject(3.14)
    assert obj


def test_instanciation_with_int():
    obj = PrimitiveFloatObject(1)
    assert obj


def test_float_and_int():
    ast = lex_and_parse("""(|
        add = (||
            1.5 + 1
        )
    |) add""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()
    assert interpreter.process.result == PrimitiveFloatObject(2.5)


def test_int_and_float():
    ast = lex_and_parse("""(|
        add = (||
            1 + 1.5
        )
    |) add""")

    context = ast[0].compile(CodeContext())
    interpreter = Interpreter(universe=get_primitives(), code_context=context)

    interpreter.interpret()
    assert interpreter.process.result == PrimitiveFloatObject(2.5)

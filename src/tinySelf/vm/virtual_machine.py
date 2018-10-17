# -*- coding: utf-8 -*-
from rply import ParsingError

from tinySelf.parser import lex_and_parse
from tinySelf.vm.primitives import get_primitives
from tinySelf.vm.interpreter import Interpreter
from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object


def virtual_machine(source):
    universe = Object()
    universe.set_slot("primitives", get_primitives())

    ast = lex_and_parse(source)

    if not ast:
        return

    interpreter = Interpreter(ast.pop().compile(CodeContext()), universe)
    print interpreter.interpret().__str__()

    for item in ast:
        context = item.compile(CodeContext())
        interpreter.add_process(context)
        print interpreter.interpret().__str__()

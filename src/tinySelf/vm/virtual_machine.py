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

    interpreter = Interpreter(universe)
    for item in ast:
        context = item.compile(CodeContext())
        print interpreter.interpret(context).__str__()

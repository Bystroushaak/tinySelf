# -*- coding: utf-8 -*-
from rply import ParsingError

from tinySelf.parser import lex_and_parse
from tinySelf.vm.primitives import get_primitives
from tinySelf.vm.interpreter import Interpreter
from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object


def virtual_machine(source):
    universe = Object()
    universe.meta_add_slot("primitives", get_primitives())

    ast = lex_and_parse(source)

    if not ast:
        return

    interpreter = Interpreter(universe)

    for item in ast:
        process = interpreter.add_process(item.compile(CodeContext()))
        interpreter.interpret()
        print process.result.__str__()
        print process.finished_with_error
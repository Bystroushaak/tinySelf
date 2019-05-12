# -*- coding: utf-8 -*-
from rply import ParsingError

from tinySelf.r_io import ewriteln
from tinySelf.parser import lex_and_parse
from tinySelf.parser import lex_and_parse_as_root
from tinySelf.vm.primitives import get_primitives
from tinySelf.vm.interpreter import Interpreter
from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object


def run_stdlib(interpreter, stdlib_source, stdlib_path):
    stdlib_ast = lex_and_parse_as_root(stdlib_source)
    stdlib_process = interpreter.add_process(stdlib_ast.compile(), stdlib_path)

    interpreter.interpret()

    if stdlib_process.finished_with_error:
        ewriteln("Couldn't initialize stdlib:")
        ewriteln(stdlib_process.result.__str__())
        ewriteln("\n")

        return False

    return True


def virtual_machine(source, source_path, stdlib_source, stdlib_path):
    universe = Object()
    universe.meta_add_slot("primitives", get_primitives())

    interpreter = Interpreter(universe)

    if stdlib_source:
        if not run_stdlib(interpreter, stdlib_source, stdlib_path):
            return None, interpreter

    ast = lex_and_parse_as_root(source)
    if not ast:
        return None, interpreter

    process = interpreter.add_process(ast.compile(), source_path)
    interpreter.interpret()

    return process, interpreter

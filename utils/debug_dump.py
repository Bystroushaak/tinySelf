#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from tinySelf.parser import lex_and_parse
from tinySelf.vm.primitives import get_primitives
from tinySelf.vm.interpreter import Interpreter
from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object


if __name__ == '__main__':
    universe = Object()
    universe.meta_add_slot("primitives", get_primitives())

    with open(sys.argv[1]) as f:
        ast = lex_and_parse(f.read())

    if not ast:
        sys.exit(0)

    interpreter = Interpreter(universe)

    try:
        for item in ast:
            process = interpreter.add_process(item.compile(CodeContext()))
            interpreter.interpret()
            print process.result.__str__()
            print process.finished_with_error
    except Exception as e:
        print "Caught %s; %s" % (e.__class__.__name__, str(e))

from rpython import conftest
class o:
    view = False
    viewloops = True
conftest.option = o

from rpython.jit.metainterp.test.support import LLJitMixin

from tinySelf.parser import lex_and_parse_as_root
from tinySelf.vm.primitives import get_primitives
from tinySelf.vm.interpreter import Interpreter
from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object
from tinySelf.vm.virtual_machine import run_stdlib
import os

stdlib = os.path.join(os.path.dirname(__file__), "../objects/stdlib.tself")

with file(stdlib) as f:
    stdlib_source = f.read()


class TestLLtype(LLJitMixin):
    def test_loop(self):
        source = """
(|
    benchmark = (| i <- 0. |
        [i < 1000] whileTrue: [
            i: i + 1.
        ].
    ).
|) benchmark.
"""
        universe = Object()
        universe.meta_add_slot("primitives", get_primitives())

        interpreter = Interpreter(universe)
        run_stdlib(interpreter, stdlib_source)

        ast = lex_and_parse_as_root(source)
        if not ast:
            return None, interpreter

        code = ast.compile(CodeContext())
        interpreter.add_process(code.finalize())
        def f():
            interpreter.interpret()
            return 0
        #res = f()
        #assert res == 0
        res = self.meta_interp(f, [], listops=True, listcomp=True, backendopt=True)
        assert res == 0


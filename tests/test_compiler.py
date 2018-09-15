# -*- coding: utf-8 -*-
from tinySelf.parser import ast_tokens
from tinySelf.parser import lex_and_parse

from tinySelf.vm.code_context import CodeContext


def test_object_compilation():
    ast = lex_and_parse("""
        (|
            a = (| var | var printLine. var).
            b <- nil.
        | nil.)
    """)

    assert len(ast) == 1

    context = CodeContext()

    ast[0].compile(context)

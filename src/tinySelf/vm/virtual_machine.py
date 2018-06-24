# -*- coding: utf-8 -*-
from rply import ParsingError

from tinySelf.parser import lex_and_parse
from tinySelf.vm.primitives import get_primitives
from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object





def virtual_machine(source):
    globals_obj = Object()
    globals_obj.set_slot("primitives", get_primitives())

    ast = lex_and_parse(source)

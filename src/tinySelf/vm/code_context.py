# -*- coding: utf-8 -*-
from rply.token import BaseBox
from rpython.rlib.types import bytearray

from bytecodes import *


class LiteralBox(BaseBox):
    pass


class IntBox(LiteralBox):
    def __init__(self, value):
        self.value = value
        self.literal_type = LITERAL_TYPE_INT

    def __str__(self):
        return str(self.value)


class StrBox(LiteralBox):
    def __init__(self, value):
        self.value = value
        self.literal_type = LITERAL_TYPE_STR

    def __str__(self):
        return self.value


class ObjBox(LiteralBox):
    def __init__(self, obj):
        self.value = obj
        self.literal_type = LITERAL_TYPE_OBJ

    def __str__(self):
        if self.value.map.ast is not None:
            return self.value.map.ast.__str__()
        
        return "No obj representation"


class CodeContext(object):
    def __init__(self, scope_parent=None):
        self.bytecodes = []  # rewrite to bytearray or something like that?
        self.literals = []
        self.scope_parent = scope_parent

    def add_literal(self, literal):
        assert isinstance(literal, LiteralBox)

        self.literals.append(literal)
        return len(self.literals) - 1

    def add_literal_str(self, literal):
        return self.add_literal(StrBox(literal))

    def add_literal_int(self, literal):
        return self.add_literal(IntBox(literal))

    def add_literal_obj(self, literal):
        return self.add_literal(ObjBox(literal))

    def add_bytecode(self, bytecode):
        self.bytecodes.append(bytecode)

    def add_literal_str_push_bytecode(self, literal):
        assert isinstance(literal, str)

        index = self.add_literal_str(literal)

        self.add_bytecode(BYTECODE_PUSHLITERAL)
        self.add_bytecode(LITERAL_TYPE_STR)
        self.add_bytecode(index)

        return index

    def to_bytecode(self):
        out = '{\n"literals": {\n'
        for cnt, i in enumerate(self.literals):
            out += '    "%d": "%s",\n' % (cnt, i.__str__())
        out += '},\n\n'

        out += '"disassembled": [\n'
        instructions = []
        for instruction in disassemble(self.bytecodes[:]):
            instructions.append('    %s' % str(instruction).replace("'", '"'))
        out += ",\n".join(instructions)
        out += '\n],\n\n'

        out += '"bytecodes": {\n    %s\n}}' % str(self.bytecodes)

        return out

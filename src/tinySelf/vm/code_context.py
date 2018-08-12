# -*- coding: utf-8 -*-
from rply.token import BaseBox
from rpython.rlib.types import bytearray

from bytecodes import *


class LiteralBox(BaseBox):
    pass


class IntBox(LiteralBox):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class StrBox(LiteralBox):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class ObjBox(LiteralBox):
    def __init__(self, obj):
        self.value = obj

    def __str__(self):
        if self.value.map.ast is not None:
            return self.value.map.ast.__str__()
        
        return "No obj representation"


class CodeContext(object):
    def __init__(self):
        self.bytecodes = []  # rewrite to bytearray or something like that?
        self.literals = []

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
        out = "Literals:\n"

        for cnt, i in enumerate(self.literals):
            out += "\t%d) %s\n" % (cnt, i.__str__())

        out += "\nDisassembled:\n"

        for instruction in disassemble(self.bytecodes[:]):
            out += "\t"

            if len(instruction) == 1:
                out += instruction[0]
            else:
                out += instruction[0] + " " + ", ".join(instruction[1:])

            out += "\n"

        out += "\nBytecodes:\n"

        # for i in self.bytecodes:
        #     out += str(i) + "\n"
        #     
        out += str(self.bytecodes)

        return out

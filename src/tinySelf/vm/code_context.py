# -*- coding: utf-8 -*-
from rply.token import BaseBox
from rpython.rlib.types import bytearray


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

    def add_bytecode(self, bytecode):
        self.bytecodes.append(bytecode)

    def to_bytecode(self):
        out = "Literals:\n"

        for i in self.literals:
            out += "\t%s\n" % i.__str__()

        out += "\nBytecode:\n"

        for i in self.bytecodes:
            out += str(i) + "\n"

        return out

# -*- coding: utf-8 -*-


class CodeContext(object):
    def __init__(self):
        self.bytecodes = bytearray()
        self.literals = []

    def add_literal(self, literal):
        self.literals.append(literal)
        return len(self.literals) - 1

    def add_bytecode(self, bytecode):
        self.bytecodes.append(bytecode)

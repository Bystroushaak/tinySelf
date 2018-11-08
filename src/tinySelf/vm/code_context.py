# -*- coding: utf-8 -*-
from rply.token import BaseBox

from tinySelf.vm.bytecodes import *
from tinySelf.vm.object_layout import Object


class LiteralBox(BaseBox):
    def finalize(self):
        pass


class IntBox(LiteralBox):
    def __init__(self, value):
        assert isinstance(value, int)

        self.value = value
        self.literal_type = LITERAL_TYPE_INT

    def __str__(self):
        return str(self.value)


class StrBox(LiteralBox):
    def __init__(self, value):
        assert isinstance(value, str)

        self.value = value
        self.literal_type = LITERAL_TYPE_STR

    def __str__(self):
        return self.value


class ObjBox(LiteralBox):
    def __init__(self, obj):
        assert isinstance(obj, Object)

        self.value = obj
        self.literal_type = LITERAL_TYPE_OBJ

    def finalize(self):
        if self.value and self.value.code_context:
            self.value.code_context.finalize()

    def __str__(self):
        if self.value.ast is not None:
            return self.value.ast.__str__()

        return "No obj representation"


class CodeContext(object):
    def __init__(self):
        self.self = None
        self._finalized = False

        self.bytecodes = ""
        self._mutable_bytecodes = []

        self.str_literal_cache = {}

        self.literals = []

    def add_literal(self, literal):
        assert isinstance(literal, LiteralBox)

        self.literals.append(literal)
        return len(self.literals) - 1

    def add_literal_str(self, literal):
        index = self.str_literal_cache.get(literal, -1)
        if index > -1:
            return index

        index = self.add_literal(StrBox(literal))
        self.str_literal_cache[literal] = index

        return index

    def add_literal_int(self, literal):
        return self.add_literal(IntBox(literal))

    def add_literal_obj(self, literal):
        return self.add_literal(ObjBox(literal))

    def add_bytecode(self, bytecode):
        self._mutable_bytecodes.append(bytecode)

    def add_literal_str_push_bytecode(self, literal):
        assert isinstance(literal, str)

        index = self.add_literal_str(literal)

        self.add_bytecode(BYTECODE_PUSH_LITERAL)
        self.add_bytecode(LITERAL_TYPE_STR)
        self.add_bytecode(index)

        return index

    def finalize(self):
        if self._finalized:
            return

        # 4x as 3 is maximum length of multi-bytecode instructions
        self._mutable_bytecodes.append(BYTECODE_RETURN_TOP)
        self._mutable_bytecodes.append(BYTECODE_RETURN_TOP)
        self._mutable_bytecodes.append(BYTECODE_RETURN_TOP)
        self._mutable_bytecodes.append(BYTECODE_RETURN_TOP)

        # I would use bytearray(), but it behaves differently under rpython
        self.bytecodes = str("".join([chr(x) for x in self._mutable_bytecodes]))
        self._mutable_bytecodes = None
        self.str_literal_cache.clear()

        for item in self.literals:
            item.finalize()

        self._finalized = True

    def debug_json(self):
        out = '{\n"literals": {\n'
        for cnt, i in enumerate(self.literals):
            out += '    "%d": "%s",\n' % (cnt, i.__str__())
        out += '},\n\n'

        out += '"disassembled": [\n'
        instructions = []
        for instruction in disassemble(self.bytecodes):
            instructions.append('    %s' % str(instruction).replace("'", '"'))
        out += ",\n".join(instructions)
        out += '\n],\n\n'

        out += '"bytecodes": {\n    %s\n}}' % str([int(x) for x in self.bytecodes])

        return out

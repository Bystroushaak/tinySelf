# -*- coding: utf-8 -*-

from bytecodes import *


class Interpreter(object):
    def __init__(self, universe):
        self.universe = universe

    def interpret(self, code_obj, frame):
        bc_index = 0

        bytecode = code_obj.get_bytecode(bc_index)

        if bytecode == BYTECODE_SEND:
            self._do_send(bc_index, code_obj, frame)
        elif bytecode == BYTECODE_SELFSEND:
            self._do_selfSend(bc_index, code_obj, frame)
        elif bytecode == BYTECODE_RESEND:
            self._do_resend(bc_index, code_obj, frame)
        elif bytecode == BYTECODE_PUSHSELF:
            self._do_pushSelf(bc_index, code_obj, frame)
        elif bytecode == BYTECODE_PUSHLITERAL:
            self._do_pushLiteral(bc_index, code_obj, frame)
        elif bytecode == BYTECODE_POP:
            self._do_pop(bc_index, code_obj, frame)
        elif bytecode == BYTECODE_RETURNTOP:
            self._do_returnTop(bc_index, code_obj, frame)
        elif bytecode == BYTECODE_RETURNIMPLICIT:
            self._do_returnImplicit(bc_index, code_obj, frame)

    def _do_send(self, bc_index, code_obj, frame):
        pass

    def _do_selfSend(self, bc_index, code_obj, frame):
        pass

    def _do_resend(self, bc_index, code_obj, frame):
        pass

    def _do_pushSelf(self, bc_index, code_obj, frame):
        pass

    def _do_pushLiteral(self, bc_index, code_obj, frame):
        pass

    def _do_pop(self, bc_index, code_obj, frame):
        pass

    def _do_returnTop(self, bc_index, code_obj, frame):
        pass

    def _do_returnImplicit(self, bc_index, code_obj, frame):
        pass

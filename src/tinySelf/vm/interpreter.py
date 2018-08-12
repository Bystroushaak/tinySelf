# -*- coding: utf-8 -*-
from bytecodes import *


class Frame(object):
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()


class ScopedFrame(Frame):
    def __init__(self, lexical_scope):
        super(ScopedFrame, self).__init__()
        self.lexical_scopes = [lexical_scope]

    def lexical_scope(self):
        self.lexical_scopes[-1]

    def push_scope(self, lexical_scope):
        self.lexical_scopes.append(lexical_scope)

    def pop_scope(self):
        return self.lexical_scopes.pop()


class Interpreter(object):
    def __init__(self, universe):
        self.universe = universe

    def interpret(self, code_obj, frame):
        bc_index = 0

        while True:
            bytecode = code_obj.get_bytecode(bc_index)

            if bytecode == BYTECODE_SEND:
                bc_index = self._do_send(bc_index, code_obj, frame)
            # elif bytecode == BYTECODE_SELFSEND:
            #     self._do_selfSend(bc_index, code_obj, frame)
            # elif bytecode == BYTECODE_RESEND:
            #     self._do_resend(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_PUSHSELF:
                self._do_pushSelf(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_PUSHLITERAL:
                self._do_pushLiteral(bc_index, code_obj, frame)
            # elif bytecode == BYTECODE_POP:
            #     self._do_pop(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_RETURNTOP:
                self._do_returnTop(bc_index, code_obj, frame)
            # elif bytecode == BYTECODE_RETURNIMPLICIT:
            #     self._do_returnImplicit(bc_index, code_obj, frame)

            bc_index += 1

    def _do_send(self, bc_index, code_obj, frame):
        message_type = code_obj.get_bytecode(bc_index + 1)
        number_of_messages = code_obj.get_bytecode(bc_index + 2)

        message = frame.pop()

        parameters = []
        if message_type == SEND_TYPE_BINARY:
            parameters = [frame.pop()]
        elif message_type == SEND_TYPE_KEYWORD:
            for _ in range(number_of_messages):
                parameters.append(frame.pop())

        obj = frame.pop()

        value_of_slot = obj.get_slot(message)
        if value_of_slot is None:
            # TODO: parent lookup
            pass
        else:
            value_of_slot = obj.get_slot_from_parents(message)

        if value_of_slot.has_code():
            # TODO: support for parameters / arguments
            self.interpret(value_of_slot.map.code, Frame())
        elif value_of_slot.has_primitive_code():
            return_value = value_of_slot.map.primitive_code(*parameters)
        else:
            return_value = value_of_slot

        frame.push(return_value)

        return bc_index + 2

    # def _do_selfSend(self, bc_index, code_obj, frame):
    #     pass

    # def _do_resend(self, bc_index, code_obj, frame):
    #     pass

    def _do_pushSelf(self, bc_index, code_obj, frame):
        pass

    def _do_pushLiteral(self, bc_index, code_obj, frame):
        pass

    # def _do_pop(self, bc_index, code_obj, frame):
    #     pass

    def _do_returnTop(self, bc_index, code_obj, frame):
        pass

    # def _do_returnImplicit(self, bc_index, code_obj, frame):
    #     pass

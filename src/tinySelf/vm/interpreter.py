# -*- coding: utf-8 -*-
from collections import OrderedDict

from tinySelf.vm.bytecodes import *

from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveStrObject

from tinySelf.vm.code_context import ObjBox
from tinySelf.vm.object_layout import Object


BOXED_NIL = ObjBox(PrimitiveNilObject())


# TODO: benchmark and eventually rewrite to linked list
class Frame(object):
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def pop_or_nil(self):
        if self.stack:
            return self.pop()

        return BOXED_NIL


class Interpreter(object):
    def __init__(self, universe):
        self.universe = universe

    def interpret(self, code_obj, frame):
        bc_index = 0

        while True:
            bytecode = code_obj.get_bytecode(bc_index)

            # TODO: sort by the statistical probability of each bytecode
            if bytecode == BYTECODE_SEND:
                bc_index = self._do_send(bc_index, code_obj, frame)
            # elif bytecode == BYTECODE_SELFSEND:
            #     self._do_selfSend(bc_index, code_obj, frame)
            # elif bytecode == BYTECODE_RESEND:
            #     self._do_resend(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_PUSHSELF:
                bc_index = self._do_push_self(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_PUSHLITERAL:
                bc_index = self._do_push_literal(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_POP:
                self._do_pop(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_RETURNTOP:
                return frame.pop_or_nil()
            # elif bytecode == BYTECODE_RETURNIMPLICIT:
            #     self._do_return_implicit(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_ADD_SLOT:
                bc_index = self._do_add_slot(bc_index, code_obj, frame)

            bc_index += 1

    def _put_together_parameters(self, parameter_names, parameters):
        if len(parameter_names) < len(parameters):
            raise ValueError("Too many parameters!")

        if len(parameter_names) > len(parameters):
            for _ in range(len(parameter_names) - len(parameters)):
                parameters.append(PrimitiveNilObject())

        return [
            (parameter_name, parameters.pop(0))
            for parameter_name in parameter_names
        ]

    def _parent_lookup(self, obj, message_name):
        pass

    def _do_send(self, bc_index, code_obj, frame):
        """
        Args:
            bc_index (int): Index of the bytecode in `code_obj` bytecode list.
            code_obj (obj): :class:`CodeContext` instance.
            frame (obj): :class:`Frame` instance.

        Returns:
            int: Index of next bytecode.
        """
        message_type = code_obj.get_bytecode(bc_index + 1)
        number_of_parameters = code_obj.get_bytecode(bc_index + 2)

        boxed_message = frame.pop()
        message_name = boxed_message.value  # unpack from StrBox

        parameters_values = []
        if message_type == SEND_TYPE_BINARY:
            parameters_values = [frame.pop()]
        elif message_type == SEND_TYPE_KEYWORD:
            for _ in range(number_of_parameters):
                parameters_values.append(frame.pop())

        obj = frame.pop()

        value_of_slot = obj.get_slot(message_name)
        if value_of_slot is None:
            # TODO: parent lookup
            value_of_slot = obj.get_slot_from_parents(message_name)

        if value_of_slot is None:
            raise ValueError("TODO: not implemented yet (missing slot err)")

        if value_of_slot.has_code:
            # inject the universe to the unscoped parents
            if code_obj.scope_parent is None:
                scope_parent = self.universe
            else:
                scope_parent = code_obj.scope_parent

            if parameters_values:
                intermediate_obj = Object()
                intermediate_obj.meta_add_parent("*", scope_parent)

                parameter_pairs = self._put_together_parameters(
                    parameter_names=value_of_slot.map.parameters,
                    parameters=parameters_values
                )
                for name, value in parameter_pairs:
                    intermediate_obj.meta_add_slot(name, value)

                obj.map.scope_parent = intermediate_obj
            else:
                obj.map.scope_parent = scope_parent

            sub_frame = Frame()
            self.interpret(value_of_slot.map.code_context, sub_frame)

            obj.scope_parent = None
            return_value = sub_frame.pop_or_nil()

        elif value_of_slot.has_primitive_code:
            return_value = ObjBox(
                value_of_slot.map.primitive_code(*parameters_values)
            )

        else:
            return_value = ObjBox(value_of_slot)

        frame.push(return_value)

        return bc_index + 2

    # def _do_selfSend(self, bc_index, code_obj, frame):
    #     pass

    # def _do_resend(self, bc_index, code_obj, frame):
    #     pass

    def _do_push_self(self, bc_index, code_obj, frame):
        frame.push(ObjBox(code_obj.scope_parent))

        return bc_index + 1

    def _literal_to_obj(self, literal, literal_type):
        """
        Convert literal to primitive object.
        """
        if literal_type == LITERAL_TYPE_INT:
            obj = PrimitiveIntObject(literal.value)
        elif literal_type == LITERAL_TYPE_STR:
            obj = PrimitiveStrObject(literal.value)
        elif literal_type == LITERAL_TYPE_OBJ:
            obj = literal
        else:
            raise ValueError("Unknown literal type; %s" % literal_type)

        return ObjBox(obj)

    def _do_push_literal(self, bc_index, code_obj, frame):
        literal_type = code_obj.get_bytecode(bc_index + 1)
        literal_index = code_obj.get_bytecode(bc_index + 2)

        if literal_type == LITERAL_TYPE_NIL:
            literal_obj = BOXED_NIL
        else:
            literal_obj = self._literal_to_obj(
                code_obj.literals[literal_index],
                literal_type
            )

        frame.push(literal_obj)

        return bc_index + 2

    def _do_pop(self, bc_index, code_obj, frame):
        frame.pop()

        return bc_index + 1

    # def _do_return_implicit(self, bc_index, code_obj, frame):
    #     pass

    def _do_add_slot(self, bc_index, code_obj, frame):
        boxed_value = frame.pop()
        boxed_slot_name = frame.pop()
        boxed_obj = frame.pop()

        slot_type = code_obj.get_bytecode(bc_index + 1)
        if slot_type == SLOT_NORMAL:
            result = boxed_obj.value.meta_add_slot(
                slot_name=boxed_slot_name.value,
                value=boxed_value.value,
            )
        elif slot_type == SLOT_PARENT:
            result = boxed_obj.value.meta_add_parent(
                slot_name=boxed_slot_name.value,
                value=boxed_value.value,
            )
        else:
            raise ValueError("Unknown slot type in ._do_add_slot()!")

        if not result:
            raise ValueError("Couldn't add slot!")

        # keep the receiver on the top of the stack
        frame.push(boxed_obj)

        return bc_index + 1

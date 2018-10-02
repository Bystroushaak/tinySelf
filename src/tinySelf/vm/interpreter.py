# -*- coding: utf-8 -*-
from collections import OrderedDict

from tinySelf.vm.bytecodes import *

from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveStrObject
from tinySelf.vm.primitives import AssignmentPrimitive

from tinySelf.vm.object_layout import Object


NIL = PrimitiveNilObject()
ASSIGNMENT_PRIMITIVE = AssignmentPrimitive()


import logging
logging.basicConfig(
    filename='trace.log',
    level=logging.DEBUG,
    format="%(lineno)d %(funcName)s(): %(message)s"
)


# TODO: benchmark and eventually rewrite to linked list
class Frame(object):
    def __init__(self):
        self.stack = []

    def push(self, item):
        assert isinstance(item, Object)

        logging.debug("pushing %s", item)

        self.stack.append(item)

    def pop(self):
        item = self.stack.pop()

        logging.debug("pop %s", item)

        return item

    def pop_or_nil(self):
        if self.stack:
            logging.debug("pop or nil %s", self.stack[-1])
            return self.pop()

        return NIL


class Interpreter(object):
    def __init__(self, universe):
        self.universe = universe

    def interpret(self, code_obj, frame):
        bc_index = 0

        logging.debug(code_obj.debug_json())

        while True:
            bytecode = code_obj.get_bytecode(bc_index)

            logging.debug("\nFrame:")
            for i, obj in enumerate(frame.stack):
                logging.debug("\t %d) %s", i, str(obj))
            logging.debug("\n\n")

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
        logging.debug("")
        if len(parameter_names) < len(parameters):
            raise ValueError("Too many parameters!")

        if len(parameter_names) > len(parameters):
            for _ in range(len(parameter_names) - len(parameters)):
                parameters.append(PrimitiveNilObject())

        return [
            (parameter_name, parameters.pop(0))
            for parameter_name in parameter_names
        ]

    def _interpret_obj_with_code(self, code, scope_parent, method_obj, parameters):
        logging.debug("")

        if parameters:
            intermediate_obj = Object()
            intermediate_obj.meta_add_parent("*", scope_parent)

            parameter_pairs = self._put_together_parameters(
                parameter_names=method_obj.map.parameters,
                parameters=parameters
            )
            for name, value in parameter_pairs:
                intermediate_obj.meta_add_slot(name, value)

            method_obj.map.scope_parent = intermediate_obj
        else:
            method_obj.map.scope_parent = scope_parent

        code_context = method_obj.map.code_context
        code_context.self = method_obj
        code_context.scope_parent = scope_parent

        ret_val = self.interpret(code_context, Frame())

        code_context.self = None
        code_context.scope_parent = None
        method_obj.map.scope_parent = None

        return ret_val

    def _check_scope_parent(self, obj, code):
        if obj.map.scope_parent is None:
            if code.scope_parent is not None:
                obj.map.scope_parent = code.scope_parent
            else:
                obj.map.scope_parent = self.universe

    def _do_send(self, bc_index, code, frame):
        """
        Args:
            bc_index (int): Index of the bytecode in `code` bytecode list.
            code (obj): :class:`CodeContext` instance.
            frame (obj): :class:`Frame` instance.

        Returns:
            int: Index of next bytecode.
        """
        logging.debug("")
        message_type = code.get_bytecode(bc_index + 1)
        number_of_parameters = code.get_bytecode(bc_index + 2)

        parameters_values = []
        if message_type == SEND_TYPE_BINARY:
            parameters_values = [frame.pop()]
        elif message_type == SEND_TYPE_KEYWORD:
            for _ in range(number_of_parameters):
                parameters_values.append(frame.pop())

        boxed_message = frame.pop()
        message_name = boxed_message.value  # unpack from StrBox

        logging.debug("message name %s", message_name)

        obj = frame.pop()
        self._check_scope_parent(obj, code)

        value_of_slot = obj.slot_lookup(message_name)
        if value_of_slot is None:
            raise ValueError("Missing slot error: " + message_name)

        if value_of_slot.has_code:
            logging.debug("code run")
            return_value = self._interpret_obj_with_code(
                code,
                obj,
                value_of_slot,
                parameters_values,
            )

        elif value_of_slot.has_primitive_code:
            logging.debug("primitive code run")
            return_value = value_of_slot.map.primitive_code(*parameters_values)

        elif value_of_slot.is_assignment_primitive:
            logging.debug("is assignment primitive")
            if len(parameters_values) != 1:
                raise ValueError("Too many values to set!")

            assert len(message_name) > 1
            slot_name = message_name[:-1]

            ret_val = obj.set_slot(slot_name, parameters_values[0])

            if ret_val is None:
                raise ValueError("wtf? how can you set slot that isn't there?")

            return bc_index + 2

        else:
            logging.debug("is just normal value")
            return_value = value_of_slot

        frame.push(return_value)

        return bc_index + 2

    # def _do_selfSend(self, bc_index, code_obj, frame):
    #     pass

    # def _do_resend(self, bc_index, code_obj, frame):
    #     pass

    def _do_push_self(self, bc_index, code_obj, frame):
        logging.debug("")
        frame.push(code_obj.self)

        return bc_index

    def _do_push_literal(self, bc_index, code_obj, frame):
        logging.debug("")
        literal_type = code_obj.get_bytecode(bc_index + 1)
        literal_index = code_obj.get_bytecode(bc_index + 2)
        boxed_literal = code_obj.literals[literal_index]

        if literal_type == LITERAL_TYPE_NIL:
            obj = NIL
        elif literal_type == LITERAL_TYPE_ASSIGNMENT:
            obj = ASSIGNMENT_PRIMITIVE
        elif literal_type == LITERAL_TYPE_INT:
            obj = PrimitiveIntObject(boxed_literal.value)
        elif literal_type == LITERAL_TYPE_STR:
            obj = PrimitiveStrObject(boxed_literal.value)
        elif literal_type == LITERAL_TYPE_OBJ:
            obj = boxed_literal.value.literal_copy()
            if code_obj.self is None:
                code_obj.self = obj
        elif literal_type == LITERAL_TYPE_BLOCK:
            obj = boxed_literal.value.literal_copy()
            current_scope = frame.pop()
            obj.map.scope_parent = current_scope
        else:
            raise ValueError("Unknown literal type; %s" % literal_type)

        frame.push(obj)

        return bc_index + 2

    def _do_pop(self, bc_index, code_obj, frame):
        logging.debug("")
        frame.pop()

        return bc_index + 1

    # def _do_return_implicit(self, bc_index, code_obj, frame):
    #     pass

    def _do_add_slot(self, bc_index, code_obj, frame):
        logging.debug("")
        value = frame.pop()
        boxed_slot_name = frame.pop()
        obj = frame.pop()

        slot_name = boxed_slot_name.value

        slot_type = code_obj.get_bytecode(bc_index + 1)
        if slot_type == SLOT_NORMAL:
            obj.meta_add_slot(slot_name=slot_name, value=value)
        elif slot_type == SLOT_PARENT:
            obj.meta_add_parent(slot_name=slot_name, value=value)
        else:
            raise ValueError("Unknown slot type in ._do_add_slot()!")

        # keep the receiver on the top of the stack
        frame.push(obj)

        return bc_index + 1

# -*- coding: utf-8 -*-
from collections import OrderedDict

from tinySelf.vm.bytecodes import *

from tinySelf.vm.primitives import add_block_trait
from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveStrObject
from tinySelf.vm.primitives import AssignmentPrimitive

from tinySelf.vm.object_layout import Object


NIL = PrimitiveNilObject()


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


class FrameSet(object):
    def __init__(self):
        self.frame = Frame()
        self.frameset = [self.frame]

    def push_frame(self):
        self.frame = Frame()
        self.frameset.append(self.frame)

    def pop_frame(self):
        if len(self.frameset) == 1:
            return

        self.frameset.pop()
        self.frame = self.frameset[-1]

    def pop_frame_down(self):
        if len(self.frameset) == 1:
            return False

        result = self.frame.pop_or_nil()

        self.frameset.pop()
        self.frame = self.frameset[-1]

        self.frame.push(result)

        return True


class Interpreter(FrameSet):
    def __init__(self, universe):
        super(Interpreter, self).__init__()
        self.universe = universe

    def interpret(self, code_obj):
        bc_index = 0

        logging.debug(code_obj.debug_json())

        while True:
            bytecode = code_obj.get_bytecode(bc_index)

            logging.debug("\nFrame:")
            for i, obj in enumerate(self.frame.stack):
                logging.debug("\t %d) %s", i, str(obj))
            logging.debug("\n\n")

            # TODO: sort by the statistical probability of each bytecode
            if bytecode == BYTECODE_SEND:
                bc_index = self._do_send(bc_index, code_obj)
            # elif bytecode == BYTECODE_SELFSEND:
            #     self._do_selfSend(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_PUSHSELF:
                bc_index = self._do_push_self(bc_index, code_obj)
            elif bytecode == BYTECODE_PUSHLITERAL:
                bc_index = self._do_push_literal(bc_index, code_obj)
            elif bytecode == BYTECODE_POP:
                self._do_pop(bc_index, code_obj)
            elif bytecode == BYTECODE_RETURNTOP:
                return self.frame.pop_or_nil()
            # elif bytecode == BYTECODE_RETURNIMPLICIT:
            #     self._do_return_implicit(bc_index, code_obj, frame)
            elif bytecode == BYTECODE_ADD_SLOT:
                bc_index = self._do_add_slot(bc_index, code_obj)

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

    def _create_intermediate_params_obj(self, scope_parent, method_obj, parameters):
        intermediate_obj = Object()
        intermediate_obj.map.scope_parent = scope_parent

        parameter_pairs = self._put_together_parameters(
            parameter_names=method_obj.map.parameters,
            parameters=parameters
        )
        for name, value in parameter_pairs:
            intermediate_obj.meta_add_slot(name, value)

        return intermediate_obj

    def _interpret_obj_with_code(self, code, scope_parent, method_obj, parameters):
        logging.debug("")

        if parameters:
            method_obj.map.scope_parent = self._create_intermediate_params_obj(
                scope_parent,
                method_obj,
                parameters
            )
        else:
            method_obj.map.scope_parent = scope_parent

        code_context = method_obj.map.code_context
        code_context.self = method_obj
        code_context.scope_parent = scope_parent

        self.push_frame()
        ret_val = self.interpret(code_context)
        self.pop_frame()

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

    def _resend_to_parent(self, obj, parent_name, message_name):
        logging.debug("resend %s.%s" % (parent_name, message_name))

        resend_parent = obj.map.parent_slots.get(parent_name)
        if resend_parent is None and obj.map.scope_parent:
            resend_parent = obj.map.scope_parent.map.parent_slots.get(parent_name)

        if resend_parent is None:
            raise ValueError(
                "Can't do resend; parent `%s` not found!" % parent_name
            )

        return resend_parent.slot_lookup(message_name)

    def _do_send(self, bc_index, code):
        """
        Args:
            bc_index (int): Index of the bytecode in `code` bytecode list.
            code (obj): :class:`CodeContext` instance.

        Returns:
            int: Index of next bytecode.
        """
        logging.debug("")
        message_type = code.get_bytecode(bc_index + 1)
        number_of_parameters = code.get_bytecode(bc_index + 2)

        parameters_values = []
        if message_type == SEND_TYPE_BINARY:
            parameters_values = [self.frame.pop()]
        elif message_type == SEND_TYPE_KEYWORD or \
             message_type == SEND_TYPE_KEYWORD_RESEND:
            for _ in range(number_of_parameters):
                parameters_values.append(self.frame.pop())

        boxed_resend_parent_name = ""
        if message_type == SEND_TYPE_UNARY_RESEND or \
           message_type == SEND_TYPE_KEYWORD_RESEND:
            boxed_resend_parent_name = self.frame.pop()

        boxed_message = self.frame.pop()
        message_name = boxed_message.value  # unpack from StrBox

        logging.debug("message name %s", message_name)

        obj = self.frame.pop()
        self._check_scope_parent(obj, code)

        if boxed_resend_parent_name:
            parent_name = boxed_resend_parent_name.value
            slot = self._resend_to_parent(obj, parent_name, message_name)
        else:
            slot = obj.slot_lookup(message_name)

        if slot is None:
            raise ValueError("Missing slot error: " + message_name)

        if slot.has_code:
            logging.debug("code run")
            return_value = self._interpret_obj_with_code(
                code=code,
                scope_parent=obj,
                method_obj=slot,
                parameters=parameters_values,
            )

        elif slot.has_primitive_code:
            logging.debug("primitive code run")
            return_value = slot.map.primitive_code(*parameters_values)

        elif slot.is_assignment_primitive:
            logging.debug("is assignment primitive")
            if len(parameters_values) != 1:
                raise ValueError("Too many values to set!")

            assert len(message_name) > 1
            slot_name = message_name[:-1]

            assignee = slot.real_parent
            ret_val = assignee.set_slot(slot_name, parameters_values[0])

            if ret_val is None:
                raise ValueError("Mistery; a slot that was and is not any more: %s" % slot_name)

            return bc_index + 2

        else:
            logging.debug("is just normal value")
            return_value = slot

        self.frame.push(return_value)

        return bc_index + 2

    # def _do_selfSend(self, bc_index, code_obj, frame):
    #     pass

    def _do_push_self(self, bc_index, code_obj):
        logging.debug("")
        self.frame.push(code_obj.self)

        return bc_index

    def _do_push_literal(self, bc_index, code_obj):
        logging.debug("")
        literal_type = code_obj.get_bytecode(bc_index + 1)
        literal_index = code_obj.get_bytecode(bc_index + 2)
        boxed_literal = code_obj.literals[literal_index]

        if literal_type == LITERAL_TYPE_NIL:
            obj = NIL
        elif literal_type == LITERAL_TYPE_ASSIGNMENT:
            obj = AssignmentPrimitive()
        elif literal_type == LITERAL_TYPE_INT:
            obj = PrimitiveIntObject(boxed_literal.value)
        elif literal_type == LITERAL_TYPE_STR:
            obj = PrimitiveStrObject(boxed_literal.value)
        elif literal_type == LITERAL_TYPE_OBJ:
            obj = boxed_literal.value.literal_copy()
            if code_obj.self is None:
                code_obj.self = obj
        elif literal_type == LITERAL_TYPE_BLOCK:
            block = boxed_literal.value.literal_copy()
            block.map.scope_parent = self.frame.pop()
            obj = add_block_trait(block)
        else:
            raise ValueError("Unknown literal type; %s" % literal_type)

        self.frame.push(obj)

        return bc_index + 2

    def _do_pop(self, bc_index, code_obj):
        logging.debug("")
        self.frame.pop()

        return bc_index + 1

    # def _do_return_implicit(self, bc_index, code_obj, frame):
    #     pass

    def _do_add_slot(self, bc_index, code_obj):
        logging.debug("")
        value = self.frame.pop()
        boxed_slot_name = self.frame.pop()
        obj = self.frame.pop()

        slot_name = boxed_slot_name.value

        if value.is_assignment_primitive:
            value.real_parent = obj

        slot_type = code_obj.get_bytecode(bc_index + 1)
        if slot_type == SLOT_NORMAL:
            obj.meta_add_slot(slot_name=slot_name, value=value)
        elif slot_type == SLOT_PARENT:
            obj.meta_add_parent(parent_name=slot_name, value=value)
        else:
            raise ValueError("Unknown slot type in ._do_add_slot()!")

        # keep the receiver on the top of the stack
        self.frame.push(obj)

        return bc_index + 1

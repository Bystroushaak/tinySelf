# -*- coding: utf-8 -*-
from collections import OrderedDict

from tinySelf.vm.bytecodes import *

from tinySelf.vm.primitives import add_block_trait
from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveStrObject
from tinySelf.vm.primitives import AssignmentPrimitive
from tinySelf.vm.primitives import add_primitive_method

from tinySelf.vm.code_context import IntBox
from tinySelf.vm.code_context import StrBox
from tinySelf.vm.code_context import ObjBox

from tinySelf.vm.frames import ProcessStack
from tinySelf.vm.object_layout import Object


NIL = PrimitiveNilObject()


def number_of_frames(this, obj, parameters):
    return PrimitiveIntObject(len(this.frames))


def set_error_handler(this, obj, parameters):
    blck = parameters[0]
    assert isinstance(blck, Object)

    this.frame.error_handler = blck


class Interpreter(ProcessStack):
    def __init__(self, code_context, universe):
        ProcessStack.__init__(self)
        self.universe = universe
        self.frame.code_context = code_context

        self._add_reflection()

    def set_process(self, code_context):
        self.clean_frames()
        self.frame.code_context = code_context

    def _add_reflection(self):
        primitives = self.universe.get_slot("primitives")

        if primitives is None:
            primitives = Object()
            self.universe.meta_add_slot("primitives", primitives)

        interpreter = Object()
        primitives.meta_add_slot("interpreter", interpreter)

        add_primitive_method(self, interpreter, "numberOfFrames",
                             number_of_frames, [])
        add_primitive_method(self, interpreter, "setErrorHandler:",
                             set_error_handler, ["blck"])

    def interpret(self):
        while True:
            frame = self.frame
            bc_index = frame.bc_index
            code_obj = frame.code_context

            bytecode = code_obj.get_bytecode(bc_index)

            if bytecode == BYTECODE_SEND:
                bc_index += self._do_send(bc_index, code_obj)

            elif bytecode == BYTECODE_PUSHSELF:
                bc_index += self._do_push_self(bc_index, code_obj)

            elif bytecode == BYTECODE_PUSHLITERAL:
                bc_index += self._do_push_literal(bc_index, code_obj)

            elif bytecode == BYTECODE_RETURNTOP:
                if not self.is_nested_call():
                    return self.frame.pop_or_nil()

                self.pop_and_cleanup_frame()
                continue

            elif bytecode == BYTECODE_ADD_SLOT:
                bc_index += self._do_add_slot(bc_index, code_obj)

            # elif bytecode == BYTECODE_SELFSEND:
            #     self._do_selfSend(bc_index, code_obj, frame)

            # elif bytecode == BYTECODE_RETURNIMPLICIT:
            #     self._do_return_implicit(bc_index, code_obj, frame)

            else:
                raise ValueError("Unknown bytecode!")

            frame.bc_index = bc_index

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

    def _create_intermediate_params_obj(self, scope_parent, method_obj, parameters):
        intermediate_obj = Object()
        intermediate_obj.scope_parent = scope_parent

        parameter_pairs = self._put_together_parameters(
            parameter_names=method_obj.parameters,
            parameters=parameters
        )
        for name, value in parameter_pairs:
            intermediate_obj.meta_add_slot(name, value)

        return intermediate_obj

    def _push_code_obj_for_interpretation(self, code, scope_parent, method_obj, parameters):
        if parameters:
            method_obj.scope_parent = self._create_intermediate_params_obj(
                scope_parent,
                method_obj,
                parameters
            )
        else:
            method_obj.scope_parent = scope_parent

        new_code_context = method_obj.code_context
        new_code_context.self = method_obj
        new_code_context.scope_parent = scope_parent

        self.push_frame(new_code_context, method_obj)

    def _set_scope_parent_if_not_already_set(self, obj, code):
        if obj.scope_parent is None:
            if code.scope_parent is not None:
                obj.scope_parent = code.scope_parent
            else:
                obj.scope_parent = self.universe

    def _resend_to_parent(self, obj, parent_name, message_name):
        resend_parent = obj.parent_slots.get(parent_name)
        if resend_parent is None and obj.scope_parent:
            resend_parent = obj.scope_parent.parent_slots.get(parent_name)

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
        message_type = code.get_bytecode(bc_index + 1)
        number_of_parameters = code.get_bytecode(bc_index + 2)

        parameters_values = []
        if number_of_parameters > 0:
            for _ in range(number_of_parameters):
                parameters_values.append(self.frame.pop())

        boxed_resend_parent_name = None
        if message_type == SEND_TYPE_UNARY_RESEND or \
           message_type == SEND_TYPE_KEYWORD_RESEND:
            boxed_resend_parent_name = self.frame.pop()
            assert isinstance(boxed_resend_parent_name, PrimitiveStrObject)

        boxed_message = self.frame.pop()
        assert isinstance(boxed_message, PrimitiveStrObject)
        message_name = boxed_message.value  # unpack from StrBox

        obj = self.frame.pop()
        self._set_scope_parent_if_not_already_set(obj, code)

        if boxed_resend_parent_name:
            parent_name = boxed_resend_parent_name.value
            slot = self._resend_to_parent(obj, parent_name, message_name)
        else:
            slot = obj.slot_lookup(message_name)

        if slot is None:
            raise ValueError("Missing slot error: " + message_name)

        if slot.has_code:
            self._push_code_obj_for_interpretation(
                code=code,
                scope_parent=obj,
                method_obj=slot,
                parameters=parameters_values,
            )

        elif slot.has_primitive_code:
            return_value = slot.primitive_code(
                slot.primitive_code_self,
                obj,
                parameters_values
            )

            self.frame.push(return_value)

        elif slot.is_assignment_primitive:
            if len(parameters_values) != 1:
                raise ValueError("Too many values to set!")

            assert len(message_name) > 1
            slot_name = message_name[:-1]

            assignee = slot.real_parent
            ret_val = assignee.set_slot(slot_name, parameters_values[0])

            if ret_val is None:
                raise ValueError("Mistery; a slot that was and is not any more: %s" % slot_name)

        else:
            return_value = slot
            self.frame.push(return_value)

        return 3

    # def _do_selfSend(self, bc_index, code_obj, frame):
    #     pass

    def _do_push_self(self, bc_index, code_obj):
        self.frame.push(code_obj.self)

        return 1

    def _do_push_literal(self, bc_index, code_obj):
        literal_type = code_obj.get_bytecode(bc_index + 1)
        literal_index = code_obj.get_bytecode(bc_index + 2)
        boxed_literal = code_obj.literals[literal_index]

        if literal_type == LITERAL_TYPE_NIL:
            obj = NIL
        elif literal_type == LITERAL_TYPE_ASSIGNMENT:
            obj = AssignmentPrimitive()
        elif literal_type == LITERAL_TYPE_INT:
            assert isinstance(boxed_literal, IntBox)
            obj = PrimitiveIntObject(boxed_literal.value)
        elif literal_type == LITERAL_TYPE_STR:
            assert isinstance(boxed_literal, StrBox)
            obj = PrimitiveStrObject(boxed_literal.value)
        elif literal_type == LITERAL_TYPE_OBJ:
            assert isinstance(boxed_literal, ObjBox)
            obj = boxed_literal.value.literal_copy()
            if code_obj.self is None:
                code_obj.self = obj
        elif literal_type == LITERAL_TYPE_BLOCK:
            assert isinstance(boxed_literal, ObjBox)
            block = boxed_literal.value.literal_copy()
            block.scope_parent = self.frame.pop()
            obj = add_block_trait(block)
        else:
            raise ValueError("Unknown literal type; %s" % literal_type)

        self.frame.push(obj)

        return 3

    # def _do_return_implicit(self, bc_index, code_obj, frame):
    #     pass

    def _do_add_slot(self, bc_index, code_obj):
        value = self.frame.pop()
        boxed_slot_name = self.frame.pop()
        obj = self.frame.pop()

        assert isinstance(boxed_slot_name, PrimitiveStrObject)
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

        return 2

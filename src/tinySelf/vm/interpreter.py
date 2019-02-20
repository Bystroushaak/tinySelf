# -*- coding: utf-8 -*-
from collections import OrderedDict

from tinySelf.vm.bytecodes import *

from tinySelf.vm.primitives import add_block_trait
from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveStrObject
from tinySelf.vm.primitives import PrimitiveFloatObject
from tinySelf.vm.primitives import AssignmentPrimitive
from tinySelf.vm.primitives import add_primitive_method
from tinySelf.vm.primitives import gen_interpreter_primitives
from tinySelf.vm.primitives.interpreter_primitives import ErrorObject

from tinySelf.vm.code_context import IntBox
from tinySelf.vm.code_context import StrBox
from tinySelf.vm.code_context import ObjBox
from tinySelf.vm.code_context import FloatBox

from tinySelf.vm.frames import ProcessCycler
from tinySelf.vm.object_layout import Object

from rpython.rlib.jit import JitDriver


NIL = PrimitiveNilObject()
ONE_BYTECODE_LONG = 1
TWO_BYTECODES_LONG = 2
THREE_BYTECODES_LONG = 3

jitdriver = JitDriver(
    greens=['code_obj'],
    reds=['bc_index', 'bytecode', 'frame', 'self'],
    is_recursive=True  # I have no idea why is this required
)


class Interpreter(ProcessCycler):
    def __init__(self, universe, code_context=None):
        if code_context is not None:
            code_context.finalize()

        ProcessCycler.__init__(self, code_context)
        self.universe = universe
        self._add_reflection_to_universe()

    def _add_reflection_to_universe(self):
        self.universe.meta_add_slot("universe", self.universe)

        primitives = self.universe.get_slot("primitives")
        if primitives is None:
            primitives = Object()
            self.universe.meta_add_slot("primitives", primitives)

        # transport values from primitives to global level
        for slot in primitives.slot_keys:
            self.universe.meta_add_slot(slot, primitives.get_slot(slot))

        primitives.meta_add_slot("interpreter", gen_interpreter_primitives(self))

    def interpret(self):
        while self.process_count > 0:
            frame = self.process.frame
            code_obj = frame.code_context

            bytecode = ord(code_obj.bytecodes[frame.bc_index])

            bc_len = 0
            if bytecode == BYTECODE_SEND:
                bc_len = self._do_send(frame.bc_index, code_obj)

            elif bytecode == BYTECODE_PUSH_SELF:
                bc_len = self._do_push_self(frame.bc_index, code_obj)

            elif bytecode == BYTECODE_PUSH_LITERAL:
                bc_len = self._do_push_literal(frame.bc_index, code_obj)

            elif bytecode == BYTECODE_RETURN_TOP or \
                 bytecode == BYTECODE_RETURN_IMPLICIT:
                if not self.process.is_nested_call():
                    result = self.process.frame.pop_or_nil()
                    process = self.remove_active_process()

                    process.result = result
                    process.finished = True

                    if not self.has_processes_to_run():
                        self.process = process
                        return

                if bytecode == BYTECODE_RETURN_IMPLICIT:
                    self._handle_nonlocal_return()

                self.process.pop_down_and_cleanup_frame()
                self.next_process()
                continue

            elif bytecode == BYTECODE_ADD_SLOT:
                bc_len = self._do_add_slot(frame.bc_index, code_obj)

            # elif bytecode == BYTECODE_SELF_SEND:
            #     self._do_selfSend(bc_index, code_obj, frame)

            else:
                self.process.result = ErrorObject(
                    PrimitiveStrObject("Unknown bytecode: %s!" % bytecode),
                    self.process
                )
                self.process.finished = True
                self.process.finished_with_errors = True

                process = self.remove_active_process()
                if not self.has_processes_to_run():
                    self.process = process
                    return

                continue

            frame.bc_index += bc_len

            jitdriver.jit_merge_point(
                bc_index=frame.bc_index,
                bytecode=bytecode,
                code_obj=code_obj,
                frame=frame,
                self=self,
            )

            if (frame.bc_index % 10) == 0:
                self.next_process()

    def _handle_nonlocal_return(self):
        """
        If the item at the top of the process frame is block which triggered
        nonlocal return, pop frames down until you reach frame where the block
        was defined.

        Returns:
            bool: True if the nonlocal return was triggered.
        """
        method_obj = self.process.frame.tmp_method_obj_reference
        if method_obj and method_obj.is_block:
            block_scope_parent = method_obj.meta_get_parent("*")

            while block_scope_parent != method_obj:
                self.process.pop_down_and_cleanup_frame()
                method_obj = self.process.frame.tmp_method_obj_reference

    def _put_together_parameters(self, parameter_names, parameters):
        if len(parameter_names) < len(parameters):
            raise ValueError("Too many parameters!")

        if len(parameter_names) > len(parameters):
            for _ in range(len(parameter_names) - len(parameters)):
                parameters.append(PrimitiveNilObject())

        return [
            (parameter_names[i], parameters[i])
            for i in range(len(parameter_names))
        ]

    def _create_intermediate_params_obj(self, scope_parent, method_obj,
                                        parameters, prev_scope_parent=None):
        # do not create empty intermediate objects
        if not method_obj.parameters:
            # this is used to remember in what context is the block executed,
            # so in case of indirect return, it is possible to return from
            # this context and not just block
            # if method_obj.is_block and prev_scope_parent:

            if prev_scope_parent:
                method_obj.meta_add_parent("*", prev_scope_parent)

                if not method_obj.is_block and method_obj.has_code:
                    return scope_parent

                return prev_scope_parent

            return scope_parent

        intermediate_obj = Object()
        intermediate_obj.meta_add_slot("this is intermediate obj", Object())

        if scope_parent.has_parents or scope_parent.scope_parent or scope_parent.has_slots:
            intermediate_obj.scope_parent = scope_parent

        if scope_parent == method_obj:
            intermediate_obj.scope_parent = None

        if prev_scope_parent is not None:
            prev_scope_parents_parent = prev_scope_parent.meta_get_parent("*", None)
            if prev_scope_parents_parent and \
               prev_scope_parent.scope_parent == prev_scope_parents_parent.scope_parent:
                intermediate_obj.meta_add_parent("*", prev_scope_parents_parent)
            else:
                intermediate_obj.meta_add_parent("*", prev_scope_parent)

        parameter_pairs = self._put_together_parameters(
            parameter_names=method_obj.parameters,
            parameters=parameters
        )
        for name, value in parameter_pairs:
            intermediate_obj.meta_add_slot(name, value)
            intermediate_obj.meta_add_slot(
                name + ":",
                AssignmentPrimitive(intermediate_obj)
            )

        return intermediate_obj

    def _tco_applied(self, next_bytecode):
        if not (next_bytecode == BYTECODE_RETURN_TOP or \
                next_bytecode == BYTECODE_RETURN_IMPLICIT):
            return False

        self.process.pop_frame()
        return True

    def _push_code_obj_for_interpretation(self, next_bytecode, scope_parent,
                                          method_obj, parameters):
        prev_scope_parent = method_obj.scope_parent
        self._tco_applied(next_bytecode)
        method_obj.scope_parent = self._create_intermediate_params_obj(
            scope_parent=scope_parent,
            method_obj=method_obj,
            parameters=parameters,
            prev_scope_parent=prev_scope_parent,
        )

        self.process.push_frame(method_obj.code_context, method_obj)

    def _set_scope_parent_if_not_already_set(self, obj, code):
        if obj.scope_parent is None:
            obj.scope_parent = self.universe

    def _resend_to_parent(self, obj, parent_name, message_name):
        resend_parent = obj.meta_get_parent(parent_name)
        if resend_parent is None and obj.scope_parent:
            resend_parent = obj.scope_parent.meta_get_parent(parent_name)
        if resend_parent is None and "*" in obj.scope_parent.map._parent_slots:
            star_parent = obj.scope_parent.meta_get_parent("*")
            resend_parent = star_parent.meta_get_parent(parent_name)

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
        message_type = ord(code.bytecodes[bc_index + 1])
        number_of_parameters = ord(code.bytecodes[bc_index + 2])

        parameters_values = []
        if number_of_parameters > 0:
            for _ in range(number_of_parameters):
                parameters_values.append(self.process.frame.pop())

        boxed_resend_parent_name = None
        if message_type == SEND_TYPE_UNARY_RESEND or \
           message_type == SEND_TYPE_KEYWORD_RESEND:
            boxed_resend_parent_name = self.process.frame.pop()
            assert isinstance(boxed_resend_parent_name, PrimitiveStrObject)

        boxed_message = self.process.frame.pop()
        assert isinstance(boxed_message, PrimitiveStrObject)
        message_name = boxed_message.value  # unpack from StrBox

        obj = self.process.frame.pop()
        self._set_scope_parent_if_not_already_set(obj, code)

        if boxed_resend_parent_name is not None:
            parent_name = boxed_resend_parent_name.value
            slot = self._resend_to_parent(obj, parent_name, message_name)
        else:
            slot = obj.slot_lookup(message_name)

        if slot is None:
            if obj.ast:
                print "Missing slot `%s` on (line %s):" % (message_name, obj.ast.source_pos.start_line)
                print
                print obj.ast.source_pos.source_snippet
            else:
                print "Missing slot `%s`:" % message_name
                print
                print obj.__str__()

            print
            print "Failed at bytecode number %d" % bc_index
            print code.debug_repr()
            raise ValueError("Missing slot error: `%s`" % message_name)

        if slot.has_code:
            self._push_code_obj_for_interpretation(
                next_bytecode=ord(code.bytecodes[bc_index + 4]),
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

            if return_value is not None:
                self.process.frame.push(return_value)

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
            self.process.frame.push(return_value)

        return THREE_BYTECODES_LONG

    # def _do_selfSend(self, bc_index, code_obj, frame):
    #     pass

    def _do_push_self(self, bc_index, code_obj):
        self.process.frame.push(self.process.frame.self)

        return ONE_BYTECODE_LONG

    def _do_push_literal(self, bc_index, code_obj):
        literal_type = ord(code_obj.bytecodes[bc_index + 1])
        literal_index = ord(code_obj.bytecodes[bc_index + 2])
        boxed_literal = code_obj.literals[literal_index]

        if literal_type == LITERAL_TYPE_NIL:
            obj = NIL
        elif literal_type == LITERAL_TYPE_ASSIGNMENT:
            obj = AssignmentPrimitive()
        elif literal_type == LITERAL_TYPE_INT:
            assert isinstance(boxed_literal, IntBox)
            obj = PrimitiveIntObject(boxed_literal.value)
        elif literal_type == LITERAL_TYPE_FLOAT:
            assert isinstance(boxed_literal, FloatBox)
            obj = PrimitiveFloatObject(boxed_literal.value)
        elif literal_type == LITERAL_TYPE_STR:
            assert isinstance(boxed_literal, StrBox)
            obj = PrimitiveStrObject(boxed_literal.value)
        elif literal_type == LITERAL_TYPE_OBJ:
            assert isinstance(boxed_literal, ObjBox)
            obj = boxed_literal.value.literal_copy()
            if self.process.frame.self is None:
                self.process.frame.self = obj
        elif literal_type == LITERAL_TYPE_BLOCK:
            assert isinstance(boxed_literal, ObjBox)
            block = boxed_literal.value.literal_copy()
            obj = add_block_trait(block)
            block.is_block = True
            block.scope_parent = self.process.frame.pop()
        else:
            raise ValueError("Unknown literal type; %s" % literal_type)

        self.process.frame.push(obj)

        return THREE_BYTECODES_LONG

    def _do_add_slot(self, bc_index, code_obj):
        value = self.process.frame.pop()
        boxed_slot_name = self.process.frame.pop()
        obj = self.process.frame.pop()

        assert isinstance(boxed_slot_name, PrimitiveStrObject)
        slot_name = boxed_slot_name.value

        if value.is_assignment_primitive:
            value.real_parent = obj

        slot_type = ord(code_obj.bytecodes[bc_index + 1])
        if slot_type == SLOT_NORMAL:
            obj.meta_add_slot(slot_name=slot_name, value=value)
        elif slot_type == SLOT_PARENT:
            obj.meta_add_parent(parent_name=slot_name, value=value)
        else:
            raise ValueError("Unknown slot type in ._do_add_slot()!")

        # keep the receiver on the top of the stack
        self.process.frame.push(obj)

        return TWO_BYTECODES_LONG

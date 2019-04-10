# -*- coding: utf-8 -*-
from collections import OrderedDict

from rpython.rlib import jit
from rpython.rlib.objectmodel import we_are_translated

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
from tinySelf.vm.object_layout import Object, NamedCacheItem

from tinySelf.vm.dynamic_recompiler import dynamic_recompiler

if not we_are_translated():
    from tinySelf.vm.debug.visualisations import obj_map_to_plantuml
    from tinySelf.vm.debug.visualisations import process_stack_to_plantuml


NIL = PrimitiveNilObject()
ONE_BYTECODE_LONG = 1
TWO_BYTECODES_LONG = 2
THREE_BYTECODES_LONG = 3
EMPTY = Object()


jit.set_param(None, "enable_opts", "intbounds:rewrite:virtualize:string:pure:earlyforce:heap")

jitdriver = jit.JitDriver(
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
                self._recompile(code_obj, frame)
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

            elif bytecode == BYTECODE_NOP:
                frame.bc_index += 1
                continue

            elif bytecode == BYTECODE_LOCAL_SEND_UNARY:
                bc_len = self._do_local_send(frame.bc_index, code_obj, SEND_TYPE_UNARY)
            elif bytecode == BYTECODE_LOCAL_SEND_BINARY:
                bc_len = self._do_local_send(frame.bc_index, code_obj, SEND_TYPE_BINARY)
            elif bytecode == BYTECODE_LOCAL_SEND_KEYWORD:
                bc_len = self._do_local_send(frame.bc_index, code_obj, SEND_TYPE_KEYWORD)

            elif bytecode == BYTECODE_PARENT_SEND:
                bc_len = self._do_parent_send(frame.bc_index, code_obj)

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

    def _recompile(self, code_obj, frame):
        if code_obj.recompile and not code_obj.is_recompiled:
            frame.bc_index = dynamic_recompiler(
                frame.bc_index,
                code_obj,
                self.process.frame.self
            )

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

        for i in xrange(len(parameter_names)):  # TODO: benchmark rewrite to enumerate()
            yield parameter_names[i], parameters[i]

    def _create_intermediate_params_obj(self, scope_parent, method_obj,
                                        parameters, prev_scope_parent=None):
        # do not create empty intermediate objects
        if not method_obj.parameters:
            # this is used to remember in what context is the block executed,
            # so in case of indirect return, it is possible to return from
            # this context and not just block
            if prev_scope_parent:
                method_obj.meta_add_parent("*", prev_scope_parent)

                if not method_obj.is_block and method_obj.has_code:
                    return scope_parent

                return prev_scope_parent

            return scope_parent

        if method_obj.code_context._params_cache is None:
            intermediate_obj = Object()
            intermediate_obj.meta_add_slot("ThisIsIntermediateObj", intermediate_obj)
        else:
            intermediate_obj = method_obj.code_context._params_cache.clone()

        if scope_parent.has_parents or scope_parent.scope_parent or scope_parent.has_slots:
            intermediate_obj.scope_parent = None if scope_parent == method_obj else scope_parent

        if prev_scope_parent is not None:
            prev_scope_parents_parent = prev_scope_parent.meta_get_parent("*", None)
            if prev_scope_parents_parent and \
               prev_scope_parent.scope_parent == prev_scope_parents_parent.scope_parent:
                parent = prev_scope_parents_parent
            else:
                parent = prev_scope_parent

            intermediate_obj.meta_add_parent("*", parent)

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

        if method_obj.code_context._params_cache is None:
            method_obj.code_context._params_cache = intermediate_obj

        return intermediate_obj

    def _tco_applied(self, next_bytecode):
        if next_bytecode == BYTECODE_RETURN_TOP or next_bytecode == BYTECODE_RETURN_IMPLICIT:
            self.process.pop_frame()

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
        if resend_parent is None and obj.scope_parent.map._parent_slots.has_key("*"):  # TODO: rewrite
            star_parent = obj.scope_parent.meta_get_parent("*")
            resend_parent = star_parent.meta_get_parent(parent_name)

        if resend_parent is None:
            raise ValueError(
                "Can't do resend; parent `%s` not found!" % parent_name
            )

        return resend_parent.slot_lookup(message_name)

    def _handle_missing_slot(self, obj, code, message_name, bc_index):
        # TODO: rewrite from prints to something more sensible
        # TODO: interpreter error instead of exception

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

        if not we_are_translated():
            process_stack_to_plantuml(self.process)
            obj_map_to_plantuml(obj, prefix="obj_parent_map")

        raise ValueError("Missing slot error: `%s`" % message_name)

    def _read_do_send_parameters(self, bc_index, code):
        boxed_message = self.process.frame.pop()
        assert isinstance(boxed_message, PrimitiveStrObject)
        message_name = boxed_message.value  # unpack from StrBox

        parameters_values = []
        number_of_parameters = ord(code.bytecodes[bc_index + 2])
        if number_of_parameters > 0:
            for _ in range(number_of_parameters):
                parameters_values.append(self.process.frame.pop())

        boxed_resend_parent_name = None
        message_type = ord(code.bytecodes[bc_index + 1])
        if message_type == SEND_TYPE_UNARY_RESEND or \
           message_type == SEND_TYPE_KEYWORD_RESEND:
            boxed_resend_parent_name = self.process.frame.pop()
            assert isinstance(boxed_resend_parent_name, PrimitiveStrObject)

        obj = self.process.frame.pop()
        self._set_scope_parent_if_not_already_set(obj, code)

        if boxed_resend_parent_name is not None:
            parent_name = boxed_resend_parent_name.value
            slot = self._resend_to_parent(obj, parent_name, message_name)
        else:
            slot = obj.slot_lookup(message_name, local_lookup_cache=True)

        return message_name, parameters_values, obj, slot

    def _eval(self, bc_index, code, message_name, parameters, obj, slot, slot_index=-1):
        if slot is None:
            if slot_index >= 0:
                message_name = obj.map._slots.keys()[slot_index]

            return self._handle_missing_slot(obj, code, message_name, bc_index)

        if slot.has_code:
            self._push_code_obj_for_interpretation(
                next_bytecode=ord(code.bytecodes[bc_index + 4]),
                scope_parent=obj,
                method_obj=slot,
                parameters=parameters,
            )

        elif slot.has_primitive_code:
            return_value = slot.primitive_code(
                slot.primitive_code_self,
                obj,
                parameters
            )

            if return_value is not None:
                self.process.frame.push(return_value)

        elif slot.is_assignment_primitive:
            if len(parameters) != 1:
                raise ValueError("Too many values to set!")

            if slot_index >= 0:
                message_name = obj.map._slots.keys()[slot_index]

            assert len(message_name) > 1
            slot_name = message_name[:-1]

            assignee = slot.real_parent
            ret_val = assignee.set_slot(slot_name, parameters[0])

            if not ret_val:
                raise ValueError("Can't set slot %s" % slot_name)

        else:
            return_value = slot
            self.process.frame.push(return_value)

        return THREE_BYTECODES_LONG


    def _do_send(self, bc_index, code):
        """
        Args:
            bc_index (int): Index of the bytecode in `code` bytecode list.
            code (obj): :class:`CodeContext` instance.

        Returns:
            int: Index of next bytecode.
        """
        message_name, parameters, obj, slot = self._read_do_send_parameters(
            bc_index,
            code
        )

        return self._eval(bc_index, code, message_name, parameters, obj, slot)

    def _do_local_send(self, bc_index, code, send_type):
        parameters = []
        number_of_parameters = ord(code.bytecodes[bc_index + 2])
        if number_of_parameters > 0:
            for _ in range(number_of_parameters):
                parameters.append(self.process.frame.pop())

        obj = self.process.frame.pop()
        self._set_scope_parent_if_not_already_set(obj, code)

        slot_index = ord(code.bytecodes[bc_index + 1])
        slot = obj._slot_values[slot_index]

        return self._eval(bc_index, code, "", parameters, obj, slot, slot_index)

    def _do_parent_send(self, bc_index, code):
        parameters = []
        number_of_parameters = ord(code.bytecodes[bc_index + 2])
        if number_of_parameters > 0:
            for _ in range(number_of_parameters):
                parameters.append(self.process.frame.pop())

        obj = self.process.frame.pop()
        self._set_scope_parent_if_not_already_set(obj, code)

        path_index = ord(code.bytecodes[bc_index + 1])

        assert path_index >= 0
        assert len(code._parent_cache_paths) > 0
        cached_item = code._parent_cache_paths[path_index]

        if cached_item.verify_version():
            slot = cached_item.item
        else:
            print("invalidated!")
            code.invalidate_parent_lookup(cached_item.message_name)
            slot = obj.slot_lookup(cached_item.message_name, local_lookup_cache=True)

        return self._eval(bc_index, code, cached_item.message_name, parameters, obj, slot)

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
            obj = boxed_literal.value.clone()
            if self.process.frame.self is None:
                self.process.frame.self = obj
        elif literal_type == LITERAL_TYPE_BLOCK:
            assert isinstance(boxed_literal, ObjBox)
            block = boxed_literal.value.clone()
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

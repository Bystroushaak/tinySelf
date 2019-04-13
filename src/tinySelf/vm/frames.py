# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object


NIL = PrimitiveNilObject()


class MethodStack(object):
    def __init__(self, code_context, prev_stack=None):
        self.code_context = code_context

        self._stack_max_size = code_context.method_stack_size
        self._stack = [None for _ in xrange(self._stack_max_size)]
        self._length = 0

        self.prev_stack = prev_stack

        self.bc_index = 0
        self.error_handler = None
        self.self = None

        # used to remove scope parent from the method later
        self.tmp_method_obj_reference = None

    def push(self, obj):
        self._stack[self._length] = obj
        self._length += 1

    def pop(self):
        if self._length == 0:
            raise IndexError()

        self._length -= 1
        ret = self._stack[self._length]
        self._stack[self._length] = None

        return ret

    def pop_or_nil(self):
        if self._length == 0:
            return NIL

        return self.pop()


class ProcessStack(object):
    def __init__(self, code_context=None):
        self.frame = MethodStack(code_context)
        self._length = 1

        self.result = None
        self.finished = False
        self.finished_with_error = False

    def is_nested_call(self):
        return self._length > 1

    def push_frame(self, code_context, method_obj):
        self.frame = MethodStack(code_context, prev_stack=self.frame)
        self.frame.self = method_obj
        self.frame.tmp_method_obj_reference = method_obj

        self._length += 1

    def top_frame(self):
        return self.frame

    def _cleanup_frame(self):
        if self.frame.code_context:
            self.frame.code_context.self = None

        if self.frame.tmp_method_obj_reference:
            # blocks have local namespaces in scope_parents..
            if not self.frame.tmp_method_obj_reference.is_block:
                self.frame.tmp_method_obj_reference.scope_parent = None

            self.frame.tmp_method_obj_reference = None

    def pop_frame(self):
        if self._length == 1:
            return

        self.frame = self.frame.prev_stack
        self._length -= 1

    def pop_and_clean_frame(self):
        self._cleanup_frame()
        self.pop_frame()

    def pop_frame_down(self):
        if self._length == 1:
            return

        result = self.frame.pop_or_nil()

        self.frame = self.frame.prev_stack
        self._length -= 1

        self.frame.push(result)

    def pop_down_and_cleanup_frame(self):
        self._cleanup_frame()
        self.pop_frame_down()

    def as_tself_object(self):
        return Object()


class ProcessCycler:
    def __init__(self, code_context=None):
        self.cycler = 0
        self.process = None
        self.processes = []
        self.process_count = 0

        if code_context is not None:
            self.add_process(code_context)

    def add_process(self, code_context):
        assert isinstance(code_context, CodeContext)

        code_context.finalize()

        new_process = ProcessStack(code_context)
        self.processes.append(new_process)
        self.process_count += 1

        if not self.process or self.process_count <= 0:
            self.process = new_process

        return new_process

    def restore_process(self, process_stack):
        assert isinstance(process_stack, ProcessStack)

        self.processes.append(process_stack)
        self.process_count += 1

        if not self.process:
            self.process = process_stack

        return process_stack

    def has_processes_to_run(self):
        return self.process_count != 0

    def remove_process(self, process):
        self.processes.remove(process)

        self.cycler = 0
        self.process_count -= 1

        if self.processes:
            self.process = self.processes[0]
        else:
            self.process = None

        return process

    def remove_active_process(self):
        if self.process not in self.processes:
            process = self.process

            if self.processes:
                self.process = self.processes[0]

            return process

        return self.remove_process(self.process)

    def next_process(self):
        if self.process_count == 0 or self.process_count == 1:
            return

        self.process = self.processes[self.cycler]

        self.cycler += 1

        if self.cycler >= self.process_count:
            self.cycler = 0

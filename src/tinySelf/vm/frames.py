# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object


NIL = PrimitiveNilObject()


class MethodStack(object):
    def __init__(self, code_context=None):
        self.stack = []
        self.bc_index = 0
        self.code_context = code_context
        self.error_handler = None

        # used to remove scope parent from the method later
        self.tmp_method_obj_reference = None

    def push(self, item):
        assert isinstance(item, Object)
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def pop_or_nil(self):
        if self.stack:
            return self.pop()

        return NIL


class ProcessStack(object):
    def __init__(self, code_context=None):
        self.frame = MethodStack(code_context)
        self.frames = [self.frame]

        self.result = None
        self.finished = False
        self.finished_with_error = False

    def is_nested_call(self):
        return len(self.frames) > 1

    def push_frame(self, code_context, method_obj):
        self.frame = MethodStack(code_context)
        self.frame.tmp_method_obj_reference = method_obj

        self.frames.append(self.frame)

    def top_frame(self):
        return self.frames[-1]

    def pop_frame(self):
        if len(self.frames) == 1:
            return

        self.frames.pop()
        self.frame = self.top_frame()

    def pop_frame_down(self):
        if len(self.frames) == 1:
            return

        result = self.frame.pop_or_nil()

        self.frames.pop()
        self.frame = self.top_frame()

        self.frame.push(result)

    def pop_and_cleanup_frame(self):
        if self.frame.code_context:
            self.frame.code_context.self = None
            self.frame.code_context.scope_parent = None

        if self.frame.tmp_method_obj_reference:
            self.frame.tmp_method_obj_reference.scope_parent = None
            self.frame.tmp_method_obj_reference = None

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

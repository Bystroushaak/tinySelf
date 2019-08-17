# -*- coding: utf-8 -*-
from tinySelf.config import USE_LINKED_LIST_METHOD_STACK

from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object


NIL = PrimitiveNilObject()


class ObjectHolder(object):
    def __init__(self, obj, prev=None):
        self.obj = obj
        self.prev = prev


class MethodStackLinkedList(object):
    def __init__(self, code_context=None, prev_stack=None):
        self._stack = None
        self.length = 0
        self.prev_stack = prev_stack

        self.bc_index = 0
        self.code_context = code_context
        self.error_handler = None
        self.self = None
        self.source_path = ""

    def push(self, obj):
        assert isinstance(obj, Object)
        if self.length == 0:
            self._stack = ObjectHolder(obj)
            self.length = 1
            return

        self._stack = ObjectHolder(obj, prev=self._stack)
        self.length += 1

    def pop(self):
        if self.length == 0:
            raise IndexError()

        if self.length == 1:
            ret = self._stack
            self.length = 0
            self._stack = None
            return ret.obj

        ret = self._stack
        self.length -= 1
        self._stack = self._stack.prev
        return ret.obj

    def pop_or_nil(self):
        if self.length == 0:
            return NIL

        return self.pop()

    def __iter__(self):
        out = []
        item = self._stack
        while item is not None:
            out.insert(0, item.obj)
            item = item.prev

        return iter(out)


class MethodStackPreallocatedArray(object):
    def __init__(self, code_context, prev_stack=None):
        self.code_context = code_context

        self._stack_max_size = code_context.method_stack_size
        self._stack = [None for _ in xrange(self._stack_max_size)]
        self.length = 0

        self.prev_stack = prev_stack

        self.bc_index = 0
        self.error_handler = None
        self.self = None
        self.source_path = ""

    def push(self, obj):
        self._stack[self.length] = obj
        self.length += 1

    def pop(self):
        if self.length == 0:
            raise IndexError()

        self.length -= 1
        ret = self._stack[self.length]
        self._stack[self.length] = None

        return ret

    def pop_or_nil(self):
        if self.length == 0:
            return NIL

        return self.pop()

    def __iter__(self):
        return iter([x for x in self._stack if x is not None])


if USE_LINKED_LIST_METHOD_STACK:
    MethodStack = MethodStackLinkedList
else:
    MethodStack = MethodStackPreallocatedArray


class ProcessStack(object):
    def __init__(self, code_context=None, source_path=""):
        self.frame = MethodStack(code_context)
        self.frame.source_path = source_path
        self.length = 1

        self.result = None
        self.finished = False
        self.finished_with_error = False

    def is_nested_call(self):
        return self.length > 1

    def push_frame(self, code_context, method_obj):
        self.frame = MethodStack(code_context, prev_stack=self.frame)
        self.frame.self = method_obj

        self.length += 1

    def top_frame(self):
        return self.frame

    def _cleanup_frame(self):  # TODO: remove?
        if self.frame.code_context:
            self.frame.code_context.self = None

        # blocks have local namespaces in scope_parents..
        if self.frame.self and not self.frame.self.is_block:
            self.frame.self.scope_parent = None

    def pop_frame(self):
        if self.length == 1:
            return

        self.frame = self.frame.prev_stack
        self.length -= 1

    def pop_and_clean_frame(self):
        self._cleanup_frame()
        self.pop_frame()

    def pop_frame_down(self):
        if self.length == 1:
            return

        result = self.frame.pop_or_nil()

        self.frame = self.frame.prev_stack
        self.length -= 1

        self.frame.push(result)

    def pop_down_and_cleanup_frame(self, raise_err=False):
        if raise_err and self.length == 1:
            raise ValueError("Nothing to pop")

        self._cleanup_frame()
        self.pop_frame_down()

    def first_nonblock_self(self):
        self_obj = self.frame.self

        if self_obj.is_block:
            return self_obj.surrounding_object
        else:
            return self_obj

    def __iter__(self):
        out = []
        item = self.frame
        while item is not None:
            out.insert(0, item)
            item = item.prev_stack

        return iter(out)


class ProcessCycler:
    def __init__(self, code_context=None):
        self.stash = []

        self.cycler = 0
        self.process = None
        self.process_count = 0
        self.processes = []

        if code_context is not None:
            self.add_process(code_context)

    def add_process(self, code_context, path=""):
        assert isinstance(code_context, CodeContext)

        code_context.finalize()

        new_process = ProcessStack(code_context, path)
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
        if self.process is None:
            return None

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

    def stash_push(self):
        copy = ProcessCycler()
        copy.cycler = self.cycler
        copy.process = self.process
        copy.process_count = self.process_count
        copy.processes = self.processes

        self.stash.append(copy)

        self.cycler = 0
        self.process = None
        self.process_count = 0
        self.processes = []

    def stash_pop(self):
        copy = self.stash.pop()

        self.cycler = copy.cycler
        self.process = copy.process
        self.process_count = copy.process_count
        self.processes = copy.processes

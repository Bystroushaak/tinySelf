# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives import PrimitiveNilObject


NIL = PrimitiveNilObject()


class Frame(object):
    def __init__(self):
        self.stack = []
        self.bc_index = 0
        self.code_context = None

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


class FrameSet(object):
    def __init__(self):
        self.clean_frames()

    def is_nested_call(self):
        return len(self.frameset) > 1

    def push_frame(self, code_context, method_obj):
        self.frame = Frame()
        self.frame.code_context = code_context
        self.frame.tmp_method_obj_reference = method_obj

        self.frameset.append(self.frame)

    def top_frame(self):
        return self.frameset[-1]

    def pop_frame(self):
        if len(self.frameset) == 1:
            return

        self.frameset.pop()
        self.frame = self.top_frame()

    def pop_frame_down(self):
        if len(self.frameset) == 1:
            return

        result = self.frame.pop_or_nil()

        self.frameset.pop()
        self.frame = self.top_frame()

        self.frame.push(result)

    def pop_and_cleanup_frame(self):
        self.frame.code_context.self = None
        self.frame.code_context.scope_parent = None

        self.frame.tmp_method_obj_reference.scope_parent = None
        self.frame.tmp_method_obj_reference = None

        self.pop_frame_down()

    def clean_frames(self):
        self.frame = Frame()
        self.frameset = [self.frame]

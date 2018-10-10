# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives import PrimitiveNilObject


NIL = PrimitiveNilObject()


# TODO: benchmark and eventually rewrite to linked list
class Frame(object):
    def __init__(self):
        self.stack = []

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

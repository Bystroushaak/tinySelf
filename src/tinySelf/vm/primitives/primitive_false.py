# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object


class PrimitiveFalseObjectSingleton(Object):
    def __init__(self):
        Object.__init__(self)

    def clone(self):
        return self

    def __str__(self):
        return "false"

    def __eq__(self, obj):
        return isinstance(obj, PrimitiveFalseObjectSingleton)


_FALSE_OBJ = PrimitiveFalseObjectSingleton()
def PrimitiveFalseObject(*args):
    return _FALSE_OBJ

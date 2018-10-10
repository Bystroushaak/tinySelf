# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object


class PrimitiveNilObjectSingleton(Object):
    def __init__(self):
        Object.__init__(self)

    def clone(self):
        return self

    def __str__(self):
        return "nil"

    def __eq__(self, obj):
        return isinstance(obj, PrimitiveNilObjectSingleton)


_NIL_OBJ = PrimitiveNilObjectSingleton()
def PrimitiveNilObject(*args):
    return _NIL_OBJ

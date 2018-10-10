# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object


class PrimitiveTrueObjectSingleton(Object):
    def __init__(self):
        Object.__init__(self)

    def clone(self):
        return self

    def __str__(self):
        return "true"

    def __eq__(self, obj):
        return isinstance(obj, PrimitiveTrueObjectSingleton)


_TRUE_OBJ = PrimitiveTrueObjectSingleton()
def PrimitiveTrueObject(*args):
    return _TRUE_OBJ

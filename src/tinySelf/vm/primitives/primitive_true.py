# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.primitive_false import PrimitiveFalseObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


def is_true(self, parameters):
    obj = parameters[0]

    if isinstance(obj, PrimitiveTrueObjectSingleton):
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


class PrimitiveTrueObjectSingleton(Object):
    def __init__(self):
        Object.__init__(self)

        add_primitive_fn(self, "is", is_true, ["obj"])

    def clone(self):
        return self

    def __str__(self):
        return "true"

    def __eq__(self, obj):
        return isinstance(obj, PrimitiveTrueObjectSingleton)


_TRUE_OBJ = PrimitiveTrueObjectSingleton()
def PrimitiveTrueObject(*args):
    return _TRUE_OBJ

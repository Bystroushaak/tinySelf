# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


def is_false(self, parameters):
    from tinySelf.vm.primitives.primitive_true import PrimitiveTrueObject
    obj = parameters[0]

    if isinstance(obj, PrimitiveFalseObjectSingleton):
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


class PrimitiveFalseObjectSingleton(Object):
    def __init__(self):
        Object.__init__(self)

        add_primitive_fn(self, "is:", is_false, ["obj"])

    def clone(self):
        return self

    def __str__(self):
        return "false"

    def __eq__(self, obj):
        return isinstance(obj, PrimitiveFalseObjectSingleton)


_FALSE_OBJ = PrimitiveFalseObjectSingleton()
def PrimitiveFalseObject(*args):
    return _FALSE_OBJ

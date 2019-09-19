# -*- coding: utf-8 -*-
from tinySelf.r_io import write

from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.primitive_true import PrimitiveTrueObject
from tinySelf.vm.primitives.primitive_false import PrimitiveFalseObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


def is_nil(interpreter, self, parameters):
    obj = parameters[0]

    if isinstance(obj, PrimitiveNilObjectSingleton):
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


class PrimitiveNilObjectSingleton(Object):
    def __init__(self):
        Object.__init__(self)

        add_primitive_fn(self, "is:", is_nil, ["obj"])

    def clone(self, copy_obj=None):
        return self

    def __str__(self):
        return "nil"

    def __eq__(self, obj):
        return isinstance(obj, PrimitiveNilObjectSingleton)


_NIL_OBJ = PrimitiveNilObjectSingleton()
def PrimitiveNilObject(*args):
    return _NIL_OBJ

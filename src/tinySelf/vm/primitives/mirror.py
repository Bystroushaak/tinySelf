# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


def primitive_add_slot(interpreter, mirror, parameters):
    assert isinstance(mirror, Mirror)
    name = parameters[0]
    assert isinstance(name, PrimitiveStrObject)
    val = parameters[1]
    assert isinstance(val, Object)

    mirror.obj_to_mirror.meta_add_slot(name.value, val)
    val.scope_parent = None  # old scope_parent is no longer valid

    return mirror.obj_to_mirror


class Mirror(Object):
    def __init__(self, obj_to_mirror, obj_map=None):
        Object.__init__(self, obj_map)

        assert isinstance(obj_to_mirror, Object)
        self.obj_to_mirror = obj_to_mirror

        add_primitive_fn(self, "toSlot:Add:", primitive_add_slot, ["name", "obj"])

    def __eq__(self, obj):
        if not isinstance(obj, Mirror):
            return False

        return self.obj_to_mirror is obj.obj_to_mirror

    def __str__(self):
        return "Mirror(%s)" % self.obj_to_mirror.__str__()

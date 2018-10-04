# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


def add(self, parameters):
    obj = parameters[0]
    assert isinstance(obj, PrimitiveIntObject)
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj.value, int)
    assert isinstance(self.value, int)

    return PrimitiveIntObject(self.value + obj.value)


class PrimitiveIntObject(Object):
    def __init__(self, value, obj_map=None):
        Object.__init__(self, obj_map)

        assert isinstance(value, int)
        self.value = value

        add_primitive_fn(self, "+", add, ["obj"])

    def __eq__(self, obj):
        if not hasattr(obj, "value"):
            return False

        return self.value == obj.value

    def __str__(self):
        return "PrimitiveIntObject(%d)" % self.value

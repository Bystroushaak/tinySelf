# -*- coding: utf-8 -*-
from tinySelf.r_io import write
from tinySelf.r_io import writeln

from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.primitive_nil import PrimitiveNilObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


def add_strings(_, self, parameters):
    obj = parameters[0]
    assert isinstance(obj, PrimitiveStrObject)
    assert isinstance(self, PrimitiveStrObject)
    assert isinstance(obj.value, str)
    assert isinstance(self.value, str)

    return PrimitiveStrObject(self.value + obj.value)


def print_string(_, self, parameters):
    assert isinstance(self, PrimitiveStrObject)
    assert isinstance(self.value, str)

    write(self.value)

    return PrimitiveNilObject()


class PrimitiveStrObject(Object):
    def __init__(self, value, obj_map=None):
        Object.__init__(self, obj_map)

        assert isinstance(value, str)
        self.value = value

        add_primitive_fn(self, "+", add_strings, ["obj"])
        add_primitive_fn(self, "print", print_string, [])

    def __str__(self):
        return "PrimitiveStrObject(%s)" % self.value

    def __eq__(self, obj):
        if not isinstance(obj, PrimitiveStrObject):
            return False

        return self.value == obj.value

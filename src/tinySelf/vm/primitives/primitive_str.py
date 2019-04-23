# -*- coding: utf-8 -*-
from tinySelf.r_io import write
from tinySelf.r_io import writeln

from tinySelf.parser.ast_tokens import _unescape_sequences

from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.cache import ObjCache
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
    _OBJ_CACHE = ObjCache()
    _immutable_fields_ = ["value"]
    def __init__(self, value, obj_map=None):
        Object.__init__(self, PrimitiveStrObject._OBJ_CACHE.map)

        assert isinstance(value, str)
        self.value = value

        if PrimitiveStrObject._OBJ_CACHE.map is not None:
            self._slot_values = PrimitiveStrObject._OBJ_CACHE.slots
            return

        add_primitive_fn(self, "+", add_strings, ["obj"])
        add_primitive_fn(self, "print", print_string, [])

        if PrimitiveStrObject._OBJ_CACHE.map is None:
            PrimitiveStrObject._OBJ_CACHE.store(self)

    def __str__(self):
        return "'" + _unescape_sequences(self.value) + "'"

    def __eq__(self, obj):
        if not isinstance(obj, PrimitiveStrObject):
            return False

        return self.value == obj.value

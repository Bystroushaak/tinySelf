# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.cache import ObjCache
from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


def list_clone(_, self, parameters):
    assert isinstance(self, PrimitiveListObject)

    return PrimitiveListObject(self.value[:])


def list_append(_, self, parameters):
    obj = parameters[0]
    assert isinstance(obj, Object)
    assert isinstance(self, PrimitiveListObject)

    self.value.append(obj)

    return obj


def list_at(_, self, parameters):
    obj = parameters[0]
    assert isinstance(obj, PrimitiveIntObject)
    assert isinstance(self, PrimitiveListObject)

    return self.value[obj.value]


def list_length(_, self, parameters):
    assert isinstance(self, PrimitiveListObject)

    return PrimitiveIntObject(len(self.value))


class PrimitiveListObject(Object):
    _OBJ_CACHE = ObjCache()
    _immutable_fields_ = ["value"]
    def __init__(self, value, obj_map=None):
        Object.__init__(self, PrimitiveListObject._OBJ_CACHE.map)

        assert isinstance(value, list)
        self.value = value

        if PrimitiveListObject._OBJ_CACHE.map is not None:
            self._slot_values = PrimitiveListObject._OBJ_CACHE.slots
            return

        add_primitive_fn(self, "clone", list_clone, [])
        add_primitive_fn(self, "append:", list_append, ["obj"])
        add_primitive_fn(self, "at:", list_at, ["index"])
        add_primitive_fn(self, "length", list_length, [])

        if PrimitiveListObject._OBJ_CACHE.map is None:
            PrimitiveListObject._OBJ_CACHE.store(self)

    def __str__(self):
        # return "'" + escape(self.value) + "'"
        return "[]"

    def __eq__(self, obj):
        if not isinstance(obj, PrimitiveListObject):
            return False

        return self.value == obj.value

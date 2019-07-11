# -*- coding: utf-8 -*-
from rpython.rlib import rsocket

from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.cache import ObjCache
from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


class PrimitiveINETAddress(Object):
    def __init__(self):
        pass


class PrimitiveSocketObject(Object):
    _OBJ_CACHE = ObjCache()
    _immutable_fields_ = ["value"]
    def __init__(self, value, obj_map=None):
        Object.__init__(self, PrimitiveSocketObject._OBJ_CACHE.map)

        assert isinstance(value, list)
        self.value = value

        if PrimitiveSocketObject._OBJ_CACHE.map is not None:
            self._slot_values = PrimitiveSocketObject._OBJ_CACHE.slots
            return

        # add_primitive_fn(self, "at:", list_at, ["index"])

        if PrimitiveSocketObject._OBJ_CACHE.map is None:
            PrimitiveSocketObject._OBJ_CACHE.store(self)

    def __str__(self):
        return "PrimitiveSocket()"

    def __eq__(self, obj):
        if not isinstance(obj, PrimitiveSocketObject):
            return False

        return self.value == obj.value


def get_primitive_socket():
    socket_obj = Object()

    # add_primitive_fn(socket_obj, "open:", open_socket, [""])

    return socket_obj

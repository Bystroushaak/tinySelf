# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.cache import ObjCache
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


def clone_list(_, self, parameters):
    assert isinstance(self, PrimitiveListObject)

    return PrimitiveListObject(self.value[:])


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

        add_primitive_fn(self, "clone", clone_list, [])

        if PrimitiveListObject._OBJ_CACHE.map is None:
            PrimitiveListObject._OBJ_CACHE.store(self)

    def __str__(self):
        # return "'" + escape(self.value) + "'"
        return "[]"

    def __eq__(self, obj):
        if not isinstance(obj, PrimitiveListObject):
            return False

        return self.value == obj.value

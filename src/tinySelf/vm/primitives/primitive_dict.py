# -*- coding: utf-8 -*-
from collections import OrderedDict

from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.cache import ObjCache
from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn
from tinySelf.vm.primitives.interpreter_primitives import call_tinyself_code_from_primitive


def dict_clone(interpreter, self, parameters):
    assert isinstance(self, PrimitiveDictObject)

    return PrimitiveDictObject(OrderedDict())


def dict_at(interpreter, self, parameters):
    assert isinstance(self, PrimitiveDictObject)


def dict_length(interpreter, self, parameters):
    assert isinstance(self, PrimitiveDictObject)

    return PrimitiveIntObject(len(self.value))


# TODO: FUCK! implementovat vlastni dict pro Object
def dict_at_key_put_obj(interpreter, self, parameters):
    key = parameters[0]
    obj = parameters[1]
    assert isinstance(self, PrimitiveDictObject)
    assert isinstance(key, Object)
    assert isinstance(obj, Object)


class PrimitiveDictObject(Object):
    _OBJ_CACHE = ObjCache()
    _immutable_fields_ = ["value"]
    def __init__(self, value, obj_map=None):
        Object.__init__(self, PrimitiveDictObject._OBJ_CACHE.map)

        assert isinstance(value, OrderedDict)
        self.value = value

        if PrimitiveDictObject._OBJ_CACHE.map is not None:
            self._slot_values = PrimitiveDictObject._OBJ_CACHE.slots
            return

        # add_primitive_fn(self, "at:", dict_at, ["index"])
        # add_primitive_fn(self, "at:Fail:", dict_at, ["index", "fail_block"])
        add_primitive_fn(self, "clone", dict_clone, [])
        add_primitive_fn(self, "length", dict_length, [])
        add_primitive_fn(self, "at:Put:", dict_at_key_put_obj, ["key", "obj"])

        if PrimitiveDictObject._OBJ_CACHE.map is None:
            PrimitiveDictObject._OBJ_CACHE.store(self)

    def __str__(self):
        raise NotImplementedError()  # TODO: implement

    def __eq__(self, obj):
        if not isinstance(obj, PrimitiveDictObject):
            return False

        return self.value == obj.value

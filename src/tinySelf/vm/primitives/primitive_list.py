# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.cache import ObjCache
from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn
from tinySelf.vm.primitives.interpreter_primitives import call_tinyself_code_from_primitive


def list_clone(interpreter, self, parameters):
    assert isinstance(self, PrimitiveListObject)

    return PrimitiveListObject(self.value[:])


def list_append(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(obj, Object)
    assert isinstance(self, PrimitiveListObject)

    self.value.append(obj)

    return obj


def list_at(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(obj, PrimitiveIntObject)
    assert isinstance(self, PrimitiveListObject)

    return self.value[obj.value]


def list_length(interpreter, self, parameters):
    assert isinstance(self, PrimitiveListObject)

    return PrimitiveIntObject(len(self.value))


def list_at_i_put_x(interpreter, self, parameters):
    index = parameters[0]
    obj = parameters[1]
    assert isinstance(index, PrimitiveIntObject)
    assert isinstance(obj, Object)
    assert isinstance(self, PrimitiveListObject)

    self.value[index.value] = obj

    return obj


def list_extend(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveListObject)

    if isinstance(obj, PrimitiveListObject):
        self.value.extend(obj.value)
        return self
    else:
        raise ValueError("Not implemented yet!") # TODO: implement as call to tinySelf code


def list_reverse(interpreter, self, parameters):
    pass


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
        add_primitive_fn(self, "extend:", list_extend, ["obj"])
        add_primitive_fn(self, "at:", list_at, ["index"])
        add_primitive_fn(self, "length", list_length, [])
        add_primitive_fn(self, "at:Put:", list_at_i_put_x, ["index", "obj"])

        if PrimitiveListObject._OBJ_CACHE.map is None:
            PrimitiveListObject._OBJ_CACHE.store(self)

    def __str__(self):
        # return "'" + escape(self.value) + "'"
        return "[]"

    def __eq__(self, obj):
        if not isinstance(obj, PrimitiveListObject):
            return False

        return self.value == obj.value

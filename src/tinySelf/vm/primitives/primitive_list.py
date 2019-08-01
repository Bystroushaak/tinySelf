# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.cache import ObjCache
from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject
from tinySelf.vm.primitives.primitive_true import PrimitiveTrueObject
from tinySelf.vm.primitives.primitive_false import PrimitiveFalseObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


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

    return self.value[int(obj.value)]


def list_length(interpreter, self, parameters):
    assert isinstance(self, PrimitiveListObject)

    return PrimitiveIntObject(len(self.value))


def list_at_i_put_x(interpreter, self, parameters):
    index = parameters[0]
    obj = parameters[1]
    assert isinstance(index, PrimitiveIntObject)
    assert isinstance(obj, Object)
    assert isinstance(self, PrimitiveListObject)

    self.value[int(index.value)] = obj

    return obj


def list_extend(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveListObject)

    if isinstance(obj, PrimitiveListObject):
        self.value.extend(obj.value)
        return self
    else:
        raise ValueError("Not implemented yet!") # TODO: implement as call to tinySelf code


def list_reversed(interpreter, self, parameters):
    assert isinstance(self, PrimitiveListObject)

    return PrimitiveListObject([x for x in reversed(self.value)])


def list_eq(interpreter, pseudo_self, parameters):
    assert isinstance(pseudo_self, PrimitiveListObject)
    other = parameters[0]

    if not isinstance(other, PrimitiveListObject):
        return PrimitiveFalseObject()

    if len(pseudo_self.value) != len(other.value):
        return PrimitiveFalseObject()

    for i in range(len(pseudo_self.value)):
        # TODO: eval inside tinySelf
        if pseudo_self.value[i] != other.value[i]:
            return PrimitiveFalseObject()

    return PrimitiveTrueObject()


def list_clear(interpreter, pseudo_self, parameters):
    assert isinstance(pseudo_self, PrimitiveListObject)

    pseudo_self.value[:] = []

    return pseudo_self


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

        add_primitive_fn(self, "at:", list_at, ["index"])
        add_primitive_fn(self, "clone", list_clone, [])
        add_primitive_fn(self, "length", list_length, [])
        add_primitive_fn(self, "append:", list_append, ["obj"])
        add_primitive_fn(self, "extend:", list_extend, ["obj"])
        add_primitive_fn(self, "at:Put:", list_at_i_put_x, ["index", "obj"])
        add_primitive_fn(self, "reversed", list_reversed, [])
        add_primitive_fn(self, "clear", list_clear, [])
        add_primitive_fn(self, "==", list_eq, ["obj"])

        if PrimitiveListObject._OBJ_CACHE.map is None:
            PrimitiveListObject._OBJ_CACHE.store(self)

    def __str__(self):
        # I would use something more elegant, but rpython doesn't let me..
        items = ""
        for x in self.value:
            items += x.__str__()

        return "[%s]" % items

    def __eq__(self, obj):
        if not isinstance(obj, PrimitiveListObject):
            return False

        return self.value == obj.value

# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


def _assert_primitive_ints(first, second):
    assert isinstance(first, PrimitiveIntObject)
    assert isinstance(second, PrimitiveIntObject)

    assert isinstance(first.value, int)
    assert isinstance(second.value, int)


def add(self, parameters):
    obj = parameters[0]
    _assert_primitive_ints(self, obj)

    return PrimitiveIntObject(self.value + obj.value)


def substract(self, parameters):
    obj = parameters[0]
    _assert_primitive_ints(self, obj)

    return PrimitiveIntObject(self.value - obj.value)


def multiply(self, parameters):
    obj = parameters[0]
    _assert_primitive_ints(self, obj)

    return PrimitiveIntObject(self.value * obj.value)


def divide(self, parameters):
    obj = parameters[0]
    _assert_primitive_ints(self, obj)

    return PrimitiveIntObject(self.value / obj.value)


def modulo(self, parameters):
    obj = parameters[0]
    _assert_primitive_ints(self, obj)

    return PrimitiveIntObject(self.value % obj.value)


def as_string(self, parameters):
    assert isinstance(self, PrimitiveIntObject)
    return PrimitiveStrObject(str(self.value))


class PrimitiveIntObject(Object):
    def __init__(self, value, obj_map=None):
        Object.__init__(self, obj_map)

        assert isinstance(value, int)
        self.value = value

        add_primitive_fn(self, "+", add, ["obj"])
        add_primitive_fn(self, "-", substract, ["obj"])
        add_primitive_fn(self, "*", multiply, ["obj"])
        add_primitive_fn(self, "/", divide, ["obj"])
        add_primitive_fn(self, "%", modulo, ["obj"])
        add_primitive_fn(self, "asPrimitiveString", as_string, [])

    def __eq__(self, obj):
        if not hasattr(obj, "value"):
            return False

        return self.value == obj.value

    def __str__(self):
        return "PrimitiveIntObject(%d)" % self.value

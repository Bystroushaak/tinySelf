# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


def add(_, self, parameters):
    obj = parameters[0]
    # yeah, this can't be factored out, I've tried..
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, PrimitiveIntObject)
    assert isinstance(self.value, int)
    assert isinstance(obj.value, int)

    return PrimitiveIntObject(self.value + obj.value)


def substract(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, PrimitiveIntObject)
    assert isinstance(self.value, int)
    assert isinstance(obj.value, int)

    return PrimitiveIntObject(self.value - obj.value)


def multiply(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, PrimitiveIntObject)
    assert isinstance(self.value, int)
    assert isinstance(obj.value, int)

    return PrimitiveIntObject(self.value * obj.value)


def divide(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, PrimitiveIntObject)
    assert isinstance(self.value, int)
    assert isinstance(obj.value, int)

    return PrimitiveIntObject(self.value / obj.value)


def modulo(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, PrimitiveIntObject)
    assert isinstance(self.value, int)
    assert isinstance(obj.value, int)

    return PrimitiveIntObject(self.value % obj.value)


def as_string(_, self, parameters):
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
        add_primitive_fn(self, "asString", as_string, [])

    def __eq__(self, obj):
        if not hasattr(obj, "value"):
            return False

        return self.value == obj.value

    def __str__(self):
        return "PrimitiveIntObject(%d)" % self.value

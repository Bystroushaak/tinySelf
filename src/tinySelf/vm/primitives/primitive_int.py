# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject
from tinySelf.vm.primitives.primitive_true import PrimitiveTrueObject
from tinySelf.vm.primitives.primitive_false import PrimitiveFalseObject
from tinySelf.vm.primitives.primitive_float import _NumberObject
from tinySelf.vm.primitives.primitive_float import PrimitiveFloatObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn



def add(_, self, parameters):
    obj = parameters[0]
    # yeah, this can't be factored out, I've tried..
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    return obj.result_type(self.value + obj.value)


def substract(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    return obj.result_type(self.value - obj.value)


def multiply(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    return obj.result_type(self.value * obj.value)


def divide(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    return obj.result_type(self.value / obj.value)


def modulo(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, PrimitiveIntObject)

    return obj.result_type(int(self.value) % int(obj.value))


def lt(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    if self.value < obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def lte(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    if self.value <= obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def gt(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    if self.value > obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def gte(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    if self.value >= obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def compare(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    if self.value == obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def as_string(_, self, parameters):
    assert isinstance(self, PrimitiveIntObject)
    return PrimitiveStrObject(str(self.value))


def as_float(_, self, parameters):
    assert isinstance(self, PrimitiveIntObject)
    return PrimitiveFloatObject(float(self.value))


class PrimitiveIntObject(_NumberObject):
    _immutable_fields_ = ["value"]
    def __init__(self, value, obj_map=None):
        _NumberObject.__init__(self, obj_map)

        # assert isinstance(value, int)
        self.value = value

        add_primitive_fn(self, "+", add, ["obj"])
        add_primitive_fn(self, "-", substract, ["obj"])
        add_primitive_fn(self, "*", multiply, ["obj"])
        add_primitive_fn(self, "/", divide, ["obj"])
        add_primitive_fn(self, "%", modulo, ["obj"])
        add_primitive_fn(self, "<", lt, ["obj"])
        add_primitive_fn(self, "<=", lte, ["obj"])
        add_primitive_fn(self, ">", gt, ["obj"])
        add_primitive_fn(self, ">=", gte, ["obj"])
        add_primitive_fn(self, "==", compare, ["obj"])
        add_primitive_fn(self, "asString", as_string, [])
        add_primitive_fn(self, "asFloat", as_float, [])

    @property
    def float_value(self):
        return float(self.value)

    def result_type(self, val):
        return PrimitiveIntObject(val)

    def __eq__(self, obj):
        if not hasattr(obj, "value"):
            return False

        return self.value == obj.value

    def __str__(self):
        return str(int(self.value))

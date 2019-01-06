# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.primitive_true import PrimitiveTrueObject
from tinySelf.vm.primitives.primitive_false import PrimitiveFalseObject
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


class _NumberObject(Object):
    def __init__(self, obj_map=None):
        Object.__init__(self, obj_map)

    @property
    def float_value(self):
        return 0.0

    def result_type(self, val):
        return _NumberObject()

    @property
    def is_float(self):
        return False


def add(_, self, parameters):
    obj = parameters[0]

    # yeah, this can't be factored out, I've tried..
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)
    # assert isinstance(obj.float_value, float)

    return PrimitiveFloatObject(self.value + obj.float_value)


def substract(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)
    # assert isinstance(obj.float_value, float)

    return PrimitiveFloatObject(self.value - obj.float_value)


def multiply(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)
    # assert isinstance(obj.float_value, float)

    return PrimitiveFloatObject(self.value * obj.float_value)


def divide(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)
    # assert isinstance(obj.float_value, float)

    return PrimitiveFloatObject(self.value / obj.float_value)


def lt(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)
    # assert isinstance(obj.value, float)

    if self.value < obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def lte(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)
    # assert isinstance(obj.value, float)

    if self.value <= obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def gt(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)
    # assert isinstance(obj.value, float)

    if self.value > obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def gte(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)
    # assert isinstance(obj.value, float)

    if self.value >= obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def compare(_, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)
    # assert isinstance(obj._asvalue, float)

    if self.value == obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def as_string(_, self, parameters):
    assert isinstance(self, PrimitiveFloatObject)
    return PrimitiveStrObject(str(self.value))


def as_int(_, self, parameters):
    from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject

    assert isinstance(self, PrimitiveFloatObject)
    return PrimitiveIntObject(int(self.value))


class PrimitiveFloatObject(_NumberObject):
    def __init__(self, value, obj_map=None):
        _NumberObject.__init__(self, obj_map)

        self.value = value

        add_primitive_fn(self, "+", add, ["obj"])
        add_primitive_fn(self, "-", substract, ["obj"])
        add_primitive_fn(self, "*", multiply, ["obj"])
        add_primitive_fn(self, "/", divide, ["obj"])
        add_primitive_fn(self, "<", lt, ["obj"])
        add_primitive_fn(self, "<=", lte, ["obj"])
        add_primitive_fn(self, ">", gt, ["obj"])
        add_primitive_fn(self, ">=", gte, ["obj"])
        add_primitive_fn(self, "==", compare, ["obj"])
        add_primitive_fn(self, "asString", as_string, [])
        add_primitive_fn(self, "asInt", as_int, [])

    @property
    def float_value(self):
        return self.value

    def result_type(self, val):
        return PrimitiveFloatObject(val)

    def __eq__(self, obj):
        if not hasattr(obj, "value"):
            return False

        return self.value == obj.value

    def __str__(self):
        return str(self.value)

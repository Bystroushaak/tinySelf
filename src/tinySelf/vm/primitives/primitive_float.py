# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.cache import ObjCache
from tinySelf.vm.primitives.primitive_true import PrimitiveTrueObject
from tinySelf.vm.primitives.primitive_false import PrimitiveFalseObject
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


class _NumberObject(Object):
    _immutable_fields_ = ["value"]
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


def add(interpreter, self, parameters):
    obj = parameters[0]

    # yeah, this can't be factored out, I've tried..
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)

    return PrimitiveFloatObject(self.value + obj.float_value)


def substract(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)

    return PrimitiveFloatObject(self.value - obj.float_value)


def multiply(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)

    return PrimitiveFloatObject(self.value * obj.float_value)


def divide(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)

    return PrimitiveFloatObject(self.value / obj.float_value)


def lt(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)

    if self.value < obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def lte(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)

    if self.value <= obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def gt(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)

    if self.value > obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def gte(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)

    if self.value >= obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def compare(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveFloatObject)
    assert isinstance(obj, _NumberObject)
    assert isinstance(self.value, float)

    if self.value == obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def as_string(interpreter, self, parameters):
    assert isinstance(self, PrimitiveFloatObject)
    return PrimitiveStrObject(str(self.value))


def as_int(interpreter, self, parameters):
    from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject

    assert isinstance(self, PrimitiveFloatObject)
    return PrimitiveIntObject(int(self.value))


class _FloatTraitObject(Object):
    pass


FLOAT_TRAIT = _FloatTraitObject()


class PrimitiveFloatObject(_NumberObject):
    _OBJ_CACHE = ObjCache()
    _immutable_fields_ = ["value"]
    def __init__(self, value, obj_map=None):
        _NumberObject.__init__(self, PrimitiveFloatObject._OBJ_CACHE.map)

        self.value = value

        if PrimitiveFloatObject._OBJ_CACHE.is_set:
            PrimitiveFloatObject._OBJ_CACHE.restore(self)
            return

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

        self.meta_add_parent("trait", FLOAT_TRAIT)

        PrimitiveFloatObject._OBJ_CACHE.store(self)

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

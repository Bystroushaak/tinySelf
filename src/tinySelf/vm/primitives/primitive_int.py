# -*- coding: utf-8 -*-
from tinySelf.r_io import write

from tinySelf.vm import Object
from tinySelf.vm.primitives.cache import ObjCache
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject
from tinySelf.vm.primitives.primitive_true import PrimitiveTrueObject
from tinySelf.vm.primitives.primitive_false import PrimitiveFalseObject
from tinySelf.vm.primitives.primitive_float import _NumberObject
from tinySelf.vm.primitives.primitive_float import PrimitiveFloatObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


def add(interpreter, self, parameters):
    obj = parameters[0]
    # yeah, this can't be factored out, I've tried..
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    return obj.result_type(self.value + obj.value)


def substract(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    return obj.result_type(self.value - obj.value)


def multiply(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    return obj.result_type(self.value * obj.value)


def divide(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    if obj.value == 0:
        from tinySelf.vm.primitives.interpreter_primitives import primitive_fn_raise_error
        return primitive_fn_raise_error(
            interpreter,
            None,
            [PrimitiveStrObject("Division by zero.")]
        )

    return obj.result_type(self.value / obj.value)


def modulo(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, PrimitiveIntObject)

    return obj.result_type(int(self.value) % int(obj.value))


def lt(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    if self.value < obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def lte(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    if self.value <= obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def gt(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    if self.value > obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def gte(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    if self.value >= obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def compare(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(self, PrimitiveIntObject)
    assert isinstance(obj, _NumberObject)

    if self.value == obj.value:
        return PrimitiveTrueObject()
    else:
        return PrimitiveFalseObject()


def as_string(interpreter, self, parameters):
    assert isinstance(self, PrimitiveIntObject)
    return PrimitiveStrObject(str(self.value))


def as_float(interpreter, self, parameters):
    assert isinstance(self, PrimitiveIntObject)
    return PrimitiveFloatObject(float(self.value))


def print_int(interpreter, self, parameters):
    assert isinstance(self, PrimitiveIntObject)

    as_str = str(self.value)
    write(as_str)

    return PrimitiveStrObject(as_str)


class _IntTraitObject(Object):
    pass


INT_TRAIT = _IntTraitObject()


class PrimitiveIntObject(_NumberObject):
    _OBJ_CACHE = ObjCache()
    _immutable_fields_ = ["value"]
    def __init__(self, value, obj_map=None):
        _NumberObject.__init__(self, PrimitiveIntObject._OBJ_CACHE.map)

        self.value = int(value)

        if PrimitiveIntObject._OBJ_CACHE.is_set:
            PrimitiveIntObject._OBJ_CACHE.restore(self)
            return

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
        add_primitive_fn(self, "print", print_int, [])

        PrimitiveIntObject._OBJ_CACHE.store(self)

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

# -*- coding: utf-8 -*-
from collections import OrderedDict

from rpython.rlib.objectmodel import r_ordereddict

from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.cache import ObjCache
from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject
from tinySelf.vm.primitives.primitive_nil import PrimitiveNilObject
from tinySelf.vm.primitives.primitive_false import PrimitiveFalseObject
from tinySelf.vm.primitives.primitive_float import PrimitiveFloatObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn
from tinySelf.vm.primitives.interpreter_primitives import eval_immediately
from tinySelf.vm.primitives.interpreter_primitives import primitive_fn_raise_error


class GlobalContext(object):
    def __init__(self):
        self.interpreter = None
        self.hash = None
        self.scope_parent = None


GLOBAL_CONTEXT = GlobalContext()


def eq_fn(obj, other):
    interpreter = GLOBAL_CONTEXT.interpreter

    eq_slot = obj.get_slot("==")
    if eq_slot is None:
        primitive_fn_raise_error(interpreter, None,
                                 [PrimitiveStrObject("== slot not found.")])
        return False

    if eq_slot.has_primitive_code:
        result = eq_slot.primitive_code(interpreter, obj, [other])
    else:
        result = eval_immediately(
                interpreter=interpreter,
                scope_parent=GLOBAL_CONTEXT.scope_parent,
                self_obj=obj,
                method=eq_slot,
                method_parameters=[other],
                raise_exception=False
        )
        if result is None:
            return False

    if result == PrimitiveNilObject():
        return False
    if result == PrimitiveFalseObject():
        return False

    return True


def hash_fn(obj):
    hash_slot = obj.get_slot("hash")

    # compute hash from the slot names
    if hash_slot is None:
        hash = 0
        for c in "".join(obj.slot_keys):
            hash += ord(c)

        return hash

    interpreter = GLOBAL_CONTEXT.interpreter
    result = eval_immediately(
            interpreter=interpreter,
            scope_parent=GLOBAL_CONTEXT.scope_parent,
            self_obj=obj,
            method=hash_slot,
            method_parameters=[],
            raise_exception=True
    )

    if not isinstance(result, PrimitiveIntObject):
        msg = "Object's `hash` message must return int when put to dict."
        primitive_fn_raise_error(interpreter, None, [PrimitiveStrObject(msg)])
        return 1

    return result.value


ObjectDict = r_ordereddict(eq_fn, hash_fn)


def dict_clone(interpreter, self, parameters):
    assert isinstance(self, PrimitiveDictObject)

    return PrimitiveDictObject(ObjectDict.copy())


def dict_at(interpreter, self, parameters):
    key = parameters[0]
    assert isinstance(key, Object)
    assert isinstance(self, PrimitiveDictObject)

    GLOBAL_CONTEXT.interpreter = interpreter
    GLOBAL_CONTEXT.scope_parent = interpreter.process.frame.self

    result = self.value.get(key, None)

    if result is None:
        return PrimitiveNilObject()

    return result


def dict_at_fail(interpreter, self, parameters):
    key = parameters[0]
    fail = parameters[1]
    assert isinstance(key, Object)
    assert isinstance(self, PrimitiveDictObject)

    GLOBAL_CONTEXT.interpreter = interpreter
    GLOBAL_CONTEXT.scope_parent = interpreter.process.frame.self

    result = self.value.get(key, None)

    if result is None:
        return fail.get_slot("value")

    return result


def dict_length(interpreter, self, parameters):
    assert isinstance(self, PrimitiveDictObject)

    return PrimitiveIntObject(len(self.value))


def dict_at_key_put_obj(interpreter, self, parameters):
    key = parameters[0]
    obj = parameters[1]
    assert isinstance(self, PrimitiveDictObject)
    assert isinstance(key, Object)
    assert isinstance(obj, Object)

    GLOBAL_CONTEXT.interpreter = interpreter
    GLOBAL_CONTEXT.scope_parent = interpreter.process.frame.self

    self.value[key] = obj

    return obj


class PrimitiveDictObject(Object):
    _OBJ_CACHE = ObjCache()
    _immutable_fields_ = ["value"]
    def __init__(self, value, obj_map=None):
        Object.__init__(self, PrimitiveDictObject._OBJ_CACHE.map)

        self.value = value

        if PrimitiveDictObject._OBJ_CACHE.map is not None:
            self._slot_values = PrimitiveDictObject._OBJ_CACHE.slots
            return

        add_primitive_fn(self, "at:", dict_at, ["index"])
        add_primitive_fn(self, "clone", dict_clone, [])
        add_primitive_fn(self, "length", dict_length, [])
        add_primitive_fn(self, "at:Put:", dict_at_key_put_obj, ["key", "obj"])

        if PrimitiveDictObject._OBJ_CACHE.map is None:
            PrimitiveDictObject._OBJ_CACHE.store(self)

    def __str__(self):
        return "dict()"

    def __eq__(self, obj):
        if not isinstance(obj, PrimitiveDictObject):
            return False

        return self.value == obj.value

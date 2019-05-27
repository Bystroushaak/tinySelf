# -*- coding: utf-8 -*-
import pytest

from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveStrObject
from tinySelf.vm.primitives import PrimitiveTrueObject
from tinySelf.vm.primitives import PrimitiveFalseObject


def call_primitive_int_binary_op(first, op, second, equals):
    o = PrimitiveIntObject(first)

    if isinstance(equals, (int, long)):
        equals = PrimitiveIntObject(equals)

    _, primitive_slot = o.slot_lookup(op)
    assert primitive_slot.map.primitive_code
    result = primitive_slot.map.primitive_code(None, o, [PrimitiveIntObject(second)])
    assert result == equals


def test_PrimitiveIntObject_plus():
    call_primitive_int_binary_op(3, "+", 2, equals=5)


def test_PrimitiveIntObject_minus():
    call_primitive_int_binary_op(3, "-", 2, equals=1)


def test_PrimitiveIntObject_minus_negative_result():
    call_primitive_int_binary_op(3, "-", 4, equals=-1)


def test_PrimitiveIntObject_multiply():
    call_primitive_int_binary_op(3, "*", 2, equals=6)


def test_PrimitiveIntObject_divide():
    call_primitive_int_binary_op(6, "/", 2, equals=3)


def test_PrimitiveIntObject_modulo():
    call_primitive_int_binary_op(4, "%", 3, equals=1)


def test_PrimitiveIntObject_greater():
    call_primitive_int_binary_op(4, ">", 3, equals=PrimitiveTrueObject())
    call_primitive_int_binary_op(1, ">", 5, equals=PrimitiveFalseObject())
    call_primitive_int_binary_op(1, ">", 1, equals=PrimitiveFalseObject())


def test_PrimitiveIntObject_lower():
    call_primitive_int_binary_op(1, "<", 5, equals=PrimitiveTrueObject())
    call_primitive_int_binary_op(5, "<", 1, equals=PrimitiveFalseObject())
    call_primitive_int_binary_op(1, "<", 1, equals=PrimitiveFalseObject())


def test_PrimitiveIntObject_greater_or_equal():
    call_primitive_int_binary_op(5, ">=", 1, equals=PrimitiveTrueObject())
    call_primitive_int_binary_op(1, ">=", 5, equals=PrimitiveFalseObject())
    call_primitive_int_binary_op(1, ">=", 1, equals=PrimitiveTrueObject())


def test_PrimitiveIntObject_lower_or_equal():
    call_primitive_int_binary_op(1, "<=", 5, equals=PrimitiveTrueObject())
    call_primitive_int_binary_op(5, "<=", 1, equals=PrimitiveFalseObject())
    call_primitive_int_binary_op(1, "<=", 1, equals=PrimitiveTrueObject())


def test_PrimitiveIntObject_as_primitive_string():
    o = PrimitiveIntObject(2)

    _, plus_slot = o.slot_lookup("asString")
    assert plus_slot.map.primitive_code
    result = plus_slot.map.primitive_code(None, o, [])
    assert result == PrimitiveStrObject("2")
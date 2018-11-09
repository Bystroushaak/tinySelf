# -*- coding: utf-8 -*-
import pytest

from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveStrObject


def call_primitive_int_binary_op(first, op, second, equals):
    o = PrimitiveIntObject(first)

    primitive_slot = o.slot_lookup(op)
    assert primitive_slot.map.primitive_code
    result = primitive_slot.map.primitive_code(None, o, [PrimitiveIntObject(second)])
    assert result == PrimitiveIntObject(equals)


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


def test_PrimitiveIntObject_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        call_primitive_int_binary_op(3, "/", 0, equals=0)


def test_PrimitiveIntObject_modulo():
    call_primitive_int_binary_op(4, "%", 3, equals=1)


def test_PrimitiveIntObject_as_primitive_string():
    o = PrimitiveIntObject(2)

    plus_slot = o.slot_lookup("asString")
    assert plus_slot.map.primitive_code
    result = plus_slot.map.primitive_code(None, o, [])
    assert result == PrimitiveStrObject("2")
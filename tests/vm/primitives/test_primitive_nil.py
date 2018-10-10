# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.primitives import PrimitiveTrueObject
from tinySelf.vm.primitives import PrimitiveFalseObject


def test_PrimitiveNilObject():
    assert PrimitiveNilObject()


def test_PrimitiveNilObject_is():
    o = PrimitiveNilObject()

    is_slot = o.slot_lookup("is")
    result = is_slot.map.primitive_code(o, [PrimitiveNilObject()])
    assert result == PrimitiveTrueObject()

    is_slot = o.slot_lookup("is")
    result = is_slot.map.primitive_code(o, [PrimitiveIntObject(3)])
    assert result == PrimitiveFalseObject()

    is_slot = o.slot_lookup("is")
    result = is_slot.map.primitive_code(o, [PrimitiveTrueObject()])
    assert result == PrimitiveFalseObject()


def test_PrimitiveNilObject_equals():
    o = PrimitiveNilObject()

    eq_slot = o.slot_lookup("==")
    result = eq_slot.map.primitive_code(o, [PrimitiveNilObject()])
    assert result == PrimitiveTrueObject()

    eq_slot = o.slot_lookup("==")
    result = eq_slot.map.primitive_code(o, [PrimitiveIntObject(3)])
    assert result == PrimitiveFalseObject()

    eq_slot = o.slot_lookup("==")
    result = eq_slot.map.primitive_code(o, [PrimitiveTrueObject()])
    assert result == PrimitiveFalseObject()

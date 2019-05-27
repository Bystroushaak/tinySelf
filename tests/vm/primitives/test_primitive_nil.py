# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.primitives import PrimitiveTrueObject
from tinySelf.vm.primitives import PrimitiveFalseObject


def test_PrimitiveNilObject():
    assert PrimitiveNilObject()


def test_PrimitiveNilObject_is():
    o = PrimitiveNilObject()

    _, is_slot = o.slot_lookup("is:")
    result = is_slot.map.primitive_code(None, o, [PrimitiveNilObject()])
    assert result == PrimitiveTrueObject()

    _, is_slot = o.slot_lookup("is:")
    result = is_slot.map.primitive_code(None, o, [PrimitiveIntObject(3)])
    assert result == PrimitiveFalseObject()

    _, is_slot = o.slot_lookup("is:")
    result = is_slot.map.primitive_code(None, o, [PrimitiveTrueObject()])
    assert result == PrimitiveFalseObject()


def test_PrimitiveNilObject_equals():
    o = PrimitiveNilObject()

    _, eq_slot = o.slot_lookup("==")
    result = eq_slot.map.primitive_code(None, o, [PrimitiveNilObject()])
    assert result == PrimitiveTrueObject()

    _, eq_slot = o.slot_lookup("==")
    result = eq_slot.map.primitive_code(None, o, [PrimitiveIntObject(3)])
    assert result == PrimitiveFalseObject()

    _, eq_slot = o.slot_lookup("==")
    result = eq_slot.map.primitive_code(None, o, [PrimitiveTrueObject()])
    assert result == PrimitiveFalseObject()

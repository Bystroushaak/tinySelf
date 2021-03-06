# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveTrueObject
from tinySelf.vm.primitives import PrimitiveFalseObject


def test_PrimitiveTrueObject():
    assert PrimitiveTrueObject()


def test_PrimitiveTrueObject_is():
    o = PrimitiveTrueObject()

    _, is_slot = o.slot_lookup("is:")
    result = is_slot.map.primitive_code(None, o, [PrimitiveTrueObject()])
    assert result == PrimitiveTrueObject()

    _, is_slot = o.slot_lookup("is:")
    result = is_slot.map.primitive_code(None, o, [PrimitiveIntObject(3)])
    assert result == PrimitiveFalseObject()

    _, is_slot = o.slot_lookup("is:")
    result = is_slot.map.primitive_code(None, o, [PrimitiveFalseObject()])
    assert result == PrimitiveFalseObject()

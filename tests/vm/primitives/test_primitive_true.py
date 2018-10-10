# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveTrueObject
from tinySelf.vm.primitives import PrimitiveFalseObject


def test_PrimitiveTrueObject():
    assert PrimitiveTrueObject()


def test_PrimitiveTrueObject_is():
    o = PrimitiveTrueObject()

    is_slot = o.slot_lookup("is:")
    result = is_slot.map.primitive_code(o, [PrimitiveTrueObject()])
    assert result == PrimitiveTrueObject()

    is_slot = o.slot_lookup("is:")
    result = is_slot.map.primitive_code(o, [PrimitiveIntObject(3)])
    assert result == PrimitiveFalseObject()

    is_slot = o.slot_lookup("is:")
    result = is_slot.map.primitive_code(o, [PrimitiveFalseObject()])
    assert result == PrimitiveFalseObject()

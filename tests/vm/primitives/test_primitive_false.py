# -*- coding: utf-8 -*-
import pytest

from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveTrueObject
from tinySelf.vm.primitives import PrimitiveFalseObject


def test_PrimitiveFalseObject():
    assert PrimitiveFalseObject()


def test_PrimitiveFalseObject_is():
    o = PrimitiveFalseObject()

    is_slot = o.slot_lookup("is")
    result = is_slot.map.primitive_code(o, [PrimitiveFalseObject()])
    assert result == PrimitiveTrueObject()

    is_slot = o.slot_lookup("is")
    result = is_slot.map.primitive_code(o, [PrimitiveIntObject(3)])
    assert result == PrimitiveFalseObject()

    is_slot = o.slot_lookup("is")
    result = is_slot.map.primitive_code(o, [PrimitiveTrueObject()])
    assert result == PrimitiveFalseObject()

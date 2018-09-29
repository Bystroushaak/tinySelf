# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveIntObject


def test_PrimitiveIntObject():
    o = PrimitiveIntObject(3)

    plus_slot = o.slot_lookup("+")
    assert plus_slot.map.primitive_code
    assert plus_slot.map.primitive_code(PrimitiveIntObject(2)) == PrimitiveIntObject(5)

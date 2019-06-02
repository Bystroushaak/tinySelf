# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import Mirror
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveStrObject

from tinySelf.vm.object_layout import Object


def test_mirror():
    o = Object()
    m = Mirror(o)

    assert not o.slot_lookup("v")[1]

    _, add_primitive = m.slot_lookup("toSlot:Add:")
    assert add_primitive.map.primitive_code
    result = add_primitive.map.primitive_code(
        None,
        m,
        [PrimitiveStrObject("v"), PrimitiveIntObject(1)]
    )
    assert result == o

    assert o.slot_lookup("v")[1] == PrimitiveIntObject(1)

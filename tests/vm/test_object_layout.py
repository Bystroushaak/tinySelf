# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.object_layout import ObjectMap


def test_clone():
    o = Object()

    clone = o.clone()
    assert clone.map is o.map

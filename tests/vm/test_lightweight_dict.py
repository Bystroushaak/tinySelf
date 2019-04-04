# -*- coding: utf-8 -*-
from tinySelf.vm.lightweight_dict import LightWeightDict


def test_lightweight_dict_init():
    lwd = LightWeightDict()


def test_lightweight_dict_one():
    lwd = LightWeightDict()
    lwd.set("xe", 1)

    assert lwd.get("xe") == 1
    assert lwd.get("a") is None

    assert lwd.keys() == ["xe"]
    assert lwd.values() == [1]

    lwd.set("xa", 2)

    assert lwd.get("xa") == 2
    assert lwd.keys() == ["xe", "xa"]
    assert lwd.values() == [1, 2]

    lwd.set("xo", 3)
    assert lwd.get("xo") == 3
    assert lwd.keys() == ["xe", "xa", "xo"]
    assert lwd.values() == [1, 2, 3]

    lwd.delete("xe")
    assert lwd.get("xe") is None
    assert lwd.keys() == ["xa", "xo"]
    assert lwd.values() == [2, 3]


def test_lightweight_dict_four():
    lwd = LightWeightDict()
    lwd.set("a", 1)
    lwd.set("b", 2)
    lwd.set("c", 3)
    lwd.set("d", 4)

    assert lwd.get("a") == 1
    assert lwd.get("b") == 2
    assert lwd.get("c") == 3
    assert lwd.get("d") == 4
    assert lwd.get("e") == None
    assert lwd.keys() == ["a", "b", "c", "d"]
    assert lwd.values() == [1, 2, 3, 4]

    lwd.delete("b")

    assert lwd.get("a") == 1
    assert lwd.get("c") == 3
    assert lwd.get("d") == 4
    assert lwd.get("e") == None
    assert lwd.keys() == ["a", "c", "d"]
    assert lwd.values() == [1, 3, 4]


def test_lightweight_dict_four():
    lwd = LightWeightDict()
    lwd._max_array_items = 4
    lwd.set("a", 1)
    lwd.set("b", 2)
    lwd.set("c", 3)
    lwd.set("d", 4)
    lwd.set("e", 5)
    lwd.set("f", 6)

    assert lwd.get("a") == 1
    assert lwd.get("b") == 2
    assert lwd.get("c") == 3
    assert lwd.get("d") == 4
    assert lwd.get("e") == 5
    assert lwd.get("f") == 6
    assert lwd.get("g") == None
    assert lwd.keys() == ["a", "b", "c", "d", "e", "f"]
    assert lwd.values() == [1, 2, 3, 4, 5, 6]

    lwd.delete("b")

    assert lwd.get("a") == 1
    assert lwd.get("c") == 3
    assert lwd.get("d") == 4
    assert lwd.get("e") == 5
    assert lwd.get("f") == 6
    assert lwd.get("g") == None
    assert lwd.keys() == ["a", "c", "d", "e", "f"]
    assert lwd.values() == [1, 3, 4, 5, 6]

# -*- coding: utf-8 -*-
from tinySelf.vm.lightweight_dict import LightWeightDict


def test_lightweight_dict_init():
    lwd = LightWeightDict()


def test_lightweight_dict_one():
    lwd = LightWeightDict()
    lwd["xe"] = 1

    assert lwd["xe"] == 1
    assert lwd["a"] is None

    assert lwd.keys() == ["xe"]
    assert lwd.values() == [1]

    lwd["xa"] = 2

    assert lwd["xa"] == 2
    assert lwd.keys() == ["xe", "xa"]
    assert lwd.values() == [1, 2]

    lwd["xo"] = 3
    assert lwd["xo"] == 3
    assert lwd.keys() == ["xe", "xa", "xo"]
    assert lwd.values() == [1, 2, 3]

    del lwd["xe"]
    assert lwd["xe"] is None
    assert lwd.keys() == ["xa", "xo"]
    assert lwd.values() == [2, 3]


def test_lightweight_dict_four():
    lwd = LightWeightDict()
    lwd["a"] = 1
    lwd["b"] = 2
    lwd["c"] = 3
    lwd["d"] = 4

    assert lwd["a"] == 1
    assert lwd["b"] == 2
    assert lwd["c"] == 3
    assert lwd["d"] == 4
    assert lwd["e"] == None
    assert lwd.keys() == ["a", "b", "c", "d"]
    assert lwd.values() == [1, 2, 3, 4]

    del lwd["b"]

    assert lwd["a"] == 1
    assert lwd["c"] == 3
    assert lwd["d"] == 4
    assert lwd["e"] == None
    assert lwd.keys() == ["a", "c", "d"]
    assert lwd.values() == [1, 3, 4]


def test_lightweight_dict_more():
    lwd = LightWeightDict()
    lwd._max_array_items = 4
    lwd["a"] = 1
    lwd["b"] = 2
    lwd["c"] = 3
    lwd["d"] = 4
    lwd["e"] = 5
    lwd["f"] = 6

    assert lwd["a"] == 1
    assert lwd["b"] == 2
    assert lwd["c"] == 3
    assert lwd["d"] == 4
    assert lwd["e"] == 5
    assert lwd["f"] == 6
    assert lwd["g"] == None
    assert lwd.keys() == ["a", "b", "c", "d", "e", "f"]
    assert lwd.values() == [1, 2, 3, 4, 5, 6]

    del lwd["b"]

    assert lwd["a"] == 1
    assert lwd["c"] == 3
    assert lwd["d"] == 4
    assert lwd["e"] == 5
    assert lwd["f"] == 6
    assert lwd["g"] == None
    assert lwd.keys() == ["a", "c", "d", "e", "f"]
    assert lwd.values() == [1, 3, 4, 5, 6]

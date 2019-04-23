# -*- coding: utf-8 -*-
from tinySelf.shared.arrays import TwoPointerArray


def test_twopointerarray():
    tpa = TwoPointerArray(5)
    assert len(tpa) == 0

    tpa.append(1)
    assert len(tpa) == 1
    assert tpa[0] == 1

    tpa.append(2)
    tpa.append(3)
    tpa.append(4)
    tpa.append(5)
    tpa.append(6)

    assert len(tpa) == 6
    assert tpa[0] == 1
    assert tpa[1] == 2
    assert tpa[2] == 3
    assert tpa[3] == 4
    assert tpa[4] == 5
    assert tpa[5] == 6

    assert tpa.pop_last() == 6
    assert len(tpa) == 5
    assert tpa[0] == 1
    assert tpa[1] == 2
    assert tpa[2] == 3
    assert tpa[3] == 4
    assert tpa[4] == 5

    assert tpa.pop_first() == 1
    assert len(tpa) == 4
    assert tpa[0] == 2
    assert tpa[1] == 3
    assert tpa[2] == 4
    assert tpa[3] == 5

    assert tpa.to_list() == [2, 3, 4, 5]

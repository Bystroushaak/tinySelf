# -*- coding: utf-8 -*-
from pytest import raises
from pytest import fixture

from tinySelf.shared.two_pointer_array import TwoPointerArray


@fixture
def tpa() :
    return TwoPointerArray(5)


@fixture
def tpa_3() :
    tpa_obj = TwoPointerArray(10)
    tpa_obj.append(1)
    tpa_obj.append(2)
    tpa_obj.append(3)

    return tpa_obj


def test_twopointerarray_len(tpa, tpa_3):
    assert len(tpa) == 0
    assert len(tpa_3) == 3


def test_twopointerarray_append_pop_last_pop_first(tpa):
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


def test_tpa_to_list(tpa):
    tpa.append(1)
    tpa.append(2)
    tpa.append(3)
    tpa.append(4)

    assert tpa.pop_last() == 4
    assert tpa.pop_first() == 1

    assert tpa.to_list() == [2, 3]


def test_tpa_to_list3(tpa_3):
    assert tpa_3.to_list() == [1, 2, 3]

    assert tpa_3.pop_last() == 3
    assert tpa_3.pop_first() == 1

    assert tpa_3.to_list() == [2]


def test_get(tpa):
    with raises(IndexError):
        tpa[0]

    tpa.append(1)

    assert tpa[0] == 1

    with raises(IndexError):
        tpa[1]


def test_reset(tpa):
    tpa.append(1)
    tpa.append(1)
    tpa.append(1)

    tpa.pop_first()
    tpa.pop_last()
    tpa.append(1)

    tpa.reset()

    assert tpa.to_list() == []

    tpa.append(1)
    assert tpa.to_list() == [1]


def test_iter(tpa):
    tpa.append(1)
    tpa.append(2)

    out = []
    for i in tpa:
        out.append(i)

    assert out == [1, 2]

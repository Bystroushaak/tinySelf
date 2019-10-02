# -*- coding: utf-8 -*-
from pytest import raises
from pytest import fixture

from tinySelf.shared.arrays import LinkedListForObjects


@fixture
def lla() :
    return LinkedListForObjects()


def test_init(lla):
    assert len(lla) == 0

    with raises(IndexError):
        lla[0]

    with raises(IndexError):
        lla[-1]


def test_append(lla):
    lla.append(1)

    assert len(lla) == 1
    assert lla[0] == 1
    assert lla[-1] == 1

    with raises(IndexError):
        lla[1]


def test_getitem_on_index_two(lla):
    lla.append(1)
    lla.append(2)

    assert len(lla) == 2
    assert lla[0] == 1
    assert lla[1] == 2
    assert lla[-1] == 2

    with raises(IndexError):
        lla[2]

    with raises(IndexError):
        lla[-2]


def test_to_list_no_items(lla):
    assert lla.to_list() == []


def test_to_list_one_item(lla):
    lla.append(1)

    assert lla.to_list() == [1]


def test_to_list_two_items(lla):
    lla.append(1)
    lla.append(2)

    assert lla.to_list() == [1, 2]


def test_set_one_item(lla):
    with raises(IndexError):
        lla[0] = 1

    lla.append(1)
    lla[0] = 2

    assert lla[0] == 2
    assert lla[-1] == 2


def test_set_two_items(lla):
    lla.append(1)
    lla.append(2)
    lla[0] = 9
    lla[1] = 0

    assert lla[0] == 9
    assert lla[1] == 0
    assert lla[-1] == 0


def test_pop_first(lla):
    with raises(IndexError):
        lla.pop_first()

    lla.append(1)


def test_pop_last(lla):
    with raises(IndexError):
        lla.pop_first()

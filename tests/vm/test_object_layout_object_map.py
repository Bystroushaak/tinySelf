# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.object_layout import ObjectMap


def test_create_instance():
    assert ObjectMap()


def test_add_slot():
    om = ObjectMap()

    om.add_slot("test", 1)
    assert "test" in om._slots
    assert om._slots["test"] == 1


def test_remove_slot():
    om = ObjectMap()

    om.add_slot("test", 1)
    assert "test" in om._slots

    om.remove_slot("test")
    assert "test" not in om._slots

    om.remove_slot("azgabash")


def test_insert_slot():
    om = ObjectMap()

    om.add_slot("first", 1)
    om.add_slot("third", 1)
    assert om._slots.keys() == ["first", "third"]

    om.insert_slot(1, "second", 1)
    assert om._slots.keys() == ["first", "second", "third"]

    om.insert_slot(0, "zero", 1)
    assert om._slots.keys() == ["zero", "first", "second", "third"]

    om.insert_slot(10, "tenth", 1)
    assert om._slots.keys() == ["zero", "first", "second", "third", "tenth"]

    om.insert_slot(-1, "-1", 1)
    assert om._slots.keys() == ["-1", "zero", "first", "second", "third", "tenth"]


def test_set_or_add_parent():
    om = ObjectMap()
    om.add_parent("test", 1)

    assert "test" in om._parent_slots
    assert om._parent_slots["test"] == 1


def test_remove_parent():
    om = ObjectMap()

    om.add_parent("test", 1)
    assert "test" in om._parent_slots

    om.remove_parent("test")
    assert "test" not in om._parent_slots


def test_clone():
    om = ObjectMap()
    om.visited = True
    om.code_context = "code"
    om.add_slot("xex", 1)

    cloned = om.clone()
    assert not cloned.visited
    assert cloned._slots == om._slots
    assert cloned._slots is not om._slots


def test_clone_is_block():
    o = Object()
    o.is_block = True

    o.meta_add_parent("xe", Object())  # creates new map

    assert o.is_block

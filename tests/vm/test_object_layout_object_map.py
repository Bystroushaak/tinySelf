# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.object_layout import ObjectMap


def test_create_instance():
    assert ObjectMap()


def test_add_slot():
    om = ObjectMap()

    om.add_slot("test", 1)
    assert "test" in om.slots
    assert om.slots["test"] == 1


def test_remove_slot():
    om = ObjectMap()

    om.add_slot("test", 1)
    assert "test" in om.slots

    om.remove_slot("test")
    assert "test" not in om.slots

    om.remove_slot("azgabash")


def test_insert_slot():
    om = ObjectMap()

    om.add_slot("first", 1)
    om.add_slot("third", 1)
    assert om.slots.keys() == ["first", "third"]

    om.insert_slot(1, "second", 1)
    assert om.slots.keys() == ["first", "second", "third"]

    om.insert_slot(0, "zero", 1)
    assert om.slots.keys() == ["zero", "first", "second", "third"]

    om.insert_slot(10, "tenth", 1)
    assert om.slots.keys() == ["zero", "first", "second", "third", "tenth"]

    om.insert_slot(-1, "-1", 1)
    assert om.slots.keys() == ["-1", "zero", "first", "second", "third", "tenth"]


def test_add_parent():
    val = Object()

    om = ObjectMap()
    om.add_parent("test", val)

    assert "test" in om.parent_slots
    assert om.parent_slots["test"] == val


def test_remove_parent():
    om = ObjectMap()

    om.add_parent("test", Object())
    assert "test" in om.parent_slots

    om.remove_parent("test")
    assert "test" not in om.parent_slots


def test_clone():
    om = ObjectMap()
    om.visited = True
    om.code_context = "code"
    om.add_slot("xex", 1)

    cloned = om.clone()
    assert not cloned.visited
    assert cloned.slots == om.slots
    assert cloned.slots is not om.slots


def test_clone_is_block():
    o = Object()
    o.is_block = True

    o.meta_add_parent("xe", Object())  # creates new map

    assert o.is_block

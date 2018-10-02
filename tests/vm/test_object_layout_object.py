# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveStrObject
from tinySelf.vm.primitives import AssignmentPrimitive
from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object


def test_meta_add_slot():
    val = PrimitiveStrObject("xe")

    o = Object()
    assert not o.slots_references

    o.meta_add_slot("test", val)
    assert o.slots_references[0] == val


def test_set_slot():
    o = Object()

    o.meta_add_slot("test", PrimitiveStrObject("xe"))
    assert o.set_slot("test", PrimitiveStrObject("xax"))
    assert not o.set_slot("bad_slot", PrimitiveStrObject("x"))


def test_get_slot():
    o = Object()

    val = PrimitiveStrObject("xe")
    o.meta_add_slot("test", val)
    assert o.get_slot("test") is val


def test_get_slot_missing():
    assert Object().get_slot("crap") is None


def test_meta_remove_slot():
    o = Object()
    assert not o.slots_references

    o.meta_add_slot("test", Object())
    assert o.slots_references
    assert "test" in o.map.slots

    o.meta_remove_slot("test")
    assert not o.slots_references
    assert "test" not in o.map.slots


def test_meta_remove_missing_slot():
    o = Object()

    o.meta_add_slot("test", Object())
    assert not o.meta_remove_slot("x")


def test_meta_remove_slot_shift_map_pointers():
    first = PrimitiveStrObject("first")
    second = PrimitiveStrObject("second")

    o = Object()
    assert not o.slots_references

    o.meta_add_slot("first", first)
    o.meta_add_slot("second", second)

    assert o.get_slot("first") is first
    assert o.get_slot("second") is second

    o.meta_remove_slot("first")

    assert len(o.slots_references) == 1
    assert len(o.map.slots) == 1
    assert o.map.slots["second"] == 0

    assert o.get_slot("first") is None
    assert o.get_slot("second") == second


def test_meta_insert_slot():
    first = PrimitiveStrObject("first")
    second = PrimitiveStrObject("second")
    third = PrimitiveStrObject("third")

    o = Object()
    assert not o.slots_references

    o.meta_add_slot("first", first)
    o.meta_add_slot("third", third)

    assert o.get_slot("first") is first
    assert o.get_slot("third") is third

    o.meta_insert_slot(1, "second", second)
    assert o.map.slots.keys() == ["first", "second", "third"]

    # make sure that objects didn't shifted
    assert o.get_slot("first") is first
    assert o.get_slot("second") is second
    assert o.get_slot("third") is third


def test_clone():
    o = Object()
    o.meta_add_slot("test", Object())

    # clones share same map
    clone = o.clone()
    assert clone.map is o.map
    assert clone.slots_references == o.slots_references

    # clones with updated slot value share same map
    clone.set_slot("test", Object())
    assert clone.map is o.map
    assert clone.slots_references != o.slots_references

    # clones with different structure don't share maps
    clone.meta_add_slot("another", Object())
    assert clone.map is not o.map
    assert clone.slots_references != o.slots_references


def test_meta_add_parent():
    val = Object()

    o = Object()
    o.meta_add_parent("p*", val)

    assert "p*" in o.map.parent_slots


def test_get_slot_from_one_parent():
    val = PrimitiveStrObject("it is xex!")

    p = Object()
    p.meta_add_slot("xex", val)

    o = Object()
    o.meta_add_parent("p", p)

    assert o.get_slot("xex") is None
    assert o.parent_lookup("xex") is val


def test_get_slot_from_several_parents():
    """
    o.parents
    |
    |-- p <-- cycle, yay --,
    |   |-- x -> Object()  |
    |   |-- y -> Object()  |
    |   `-- z -> p --------'
    |
    `-- p3
        `-- x -> p2
                 |
                 `-- xex
    """
    val = PrimitiveStrObject("it is xex!")

    p = Object()
    p.meta_add_slot("x", Object())
    p.meta_add_slot("y", Object())
    p.meta_add_slot("z", p)  # cycle, yay!

    p2 = Object()
    p.meta_add_slot("xex", val)

    p3 = Object()
    p.meta_add_slot("x", p2)

    o = Object()
    o.meta_add_parent("p", p)
    o.meta_add_parent("p3", p3)

    assert o.get_slot("xex") is None
    assert o.parent_lookup("xex") is val


def slot_lookup():
    val = PrimitiveStrObject("it is xex!")
    flat = PrimitiveStrObject("it is flat")

    p = Object()
    p.meta_add_slot("xex", val)

    o = Object()
    o.meta_add_parent("p", p)
    o.meta_add_parent("p", flat)

    assert o.get_slot("xex") is None
    assert o.slot_lookup("xex") is val
    assert o.slot_lookup("flat") is flat


def test_slot_lookup_from_scope_parent():
    p = Object()
    val = PrimitiveStrObject("it is xex!")
    p.meta_add_slot("xex", val)

    o = Object()
    o.map.scope_parent = p

    assert o.get_slot("xex") is None
    assert o.slot_lookup("xex") is val


def test_slot_lookup_from_scope_parent_and_then_parents():
    p = Object()
    val = PrimitiveStrObject("it is xex!")
    p.meta_add_slot("a", val)

    interobj = Object()
    interobj.map.scope_parent = p

    o = Object()
    o.map.scope_parent = Object()
    o.map.scope_parent.meta_add_parent("*", interobj)

    assert o.slot_lookup("a") is val


def test_has_code():
    o = Object()
    assert not o.has_code

    o.map.code_context = CodeContext()
    assert o.has_code


def test_has_primitive_code():
    o = Object()
    assert not o.has_primitive_code

    def test(x):
        return x

    o.map.primitive_code = test
    assert o.has_primitive_code
    assert not o.is_assignment_primitive


def test_is_assignment_primitive():
    o = Object()
    assert not o.is_assignment_primitive

    o = AssignmentPrimitive()
    assert o.is_assignment_primitive
    assert not o.has_code

# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveStrObject
from tinySelf.vm.primitives import AssignmentPrimitive
from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object


def test_meta_add_slot():
    val = PrimitiveStrObject("xe")

    o = Object()
    assert not o._slot_values

    o.meta_add_slot("test", val)
    assert o._slot_values[0] == val


def test_meta_add_slot_dont_check_duplicates():
    xx = PrimitiveStrObject("xx")
    zz = PrimitiveStrObject("zz")

    o = Object()
    assert not o._slot_values

    o.meta_add_slot("xx", xx)
    o.meta_add_slot("zz", zz)
    assert len(o._slot_values) == 2

    o.meta_add_slot("xx2", xx)
    assert len(o._slot_values) == 3


# def test_meta_add_slot_do_check_duplicates():
#     xx = PrimitiveStrObject("xx")
#     zz = PrimitiveStrObject("zz")
#
#     o = Object()
#     assert not o._slot_values
#
#     o.meta_add_slot("xx", xx)
#     o.meta_add_slot("zz", zz)
#     assert len(o._slot_values) == 2
#
#     o.meta_add_slot("xx2", xx, check_duplicates=True)
#     assert len(o._slot_values) == 2


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
    assert not o._slot_values

    o.meta_add_slot("test", Object())
    assert o._slot_values
    assert "test" in o.map._slots

    o.meta_remove_slot("test")
    assert not o._slot_values
    assert "test" not in o.map._slots


def test_meta_remove_missing_slot():
    o = Object()

    o.meta_add_slot("test", Object())
    assert not o.meta_remove_slot("x")


def test_meta_remove_slot_shift_map_pointers():
    first = PrimitiveStrObject("first")
    second = PrimitiveStrObject("second")
    third = PrimitiveStrObject("third")

    o = Object()
    assert not o._slot_values

    o.meta_add_slot("first", first)
    o.meta_add_slot("second", second)
    o.meta_add_slot("third", third)

    assert o.get_slot("first") is first
    assert o.get_slot("second") is second
    assert o.get_slot("third") is third

    o.meta_remove_slot("first")

    assert len(o._slot_values) == 2
    assert len(o.map._slots) == 2
    assert o.map._slots["second"] == 0
    assert o.map._slots["third"] == 1

    assert o.get_slot("first") is None
    assert o.get_slot("second") == second
    assert o.get_slot("third") == third


def test_meta_insert_slot():
    first = PrimitiveStrObject("first")
    second = PrimitiveStrObject("second")
    third = PrimitiveStrObject("third")

    o = Object()
    assert not o._slot_values

    o.meta_add_slot("first", first)
    o.meta_add_slot("third", third)

    assert o.get_slot("first") is first
    assert o.get_slot("third") is third

    o.meta_insert_slot(1, "second", second)
    assert o.map._slots.keys() == ["first", "second", "third"]

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
    assert clone._slot_values == o._slot_values

    # clones with updated slot value share same map
    clone.set_slot("test", Object())
    assert clone.map is o.map
    assert clone._slot_values != o._slot_values

    # clones with different structure don't share maps
    clone.meta_add_slot("another", Object())
    assert clone.map is not o.map
    assert clone._slot_values != o._slot_values


def test_meta_add_parent():
    val = Object()

    o = Object()
    o.meta_add_parent("p*", val)

    assert "p*" in o.map._parent_slots
    assert val in o._parent_slot_values


def test_meta_add_parent_cloned_objects_use_same_map():
    o = Object()
    o.meta_add_parent("a", PrimitiveStrObject("value"))
    x = o.clone()

    assert "a" in o.parent_slot_keys

    assert o.map == x.map


def test_meta_add_parent_cloned_objects_dont_change_when_parent_is_changed():
    o = Object()
    o.meta_add_parent("a", PrimitiveStrObject("value"))
    x = o.clone()

    assert o.map == x.map

    x.meta_add_parent("a", PrimitiveStrObject("another"))

    assert o.map == x.map
    assert o != x


def test_meta_add_parent_structural_change_creates_new_map_add():
    o = Object()
    o.meta_add_parent("a", PrimitiveStrObject("value"))
    x = o.clone()

    assert o.map == x.map

    x.meta_add_parent("*", PrimitiveStrObject("another"))
    assert o.map != x.map
    assert o != x


def test_meta_add_parent_structural_change_creates_new_map_remove():
    o = Object()
    o.meta_add_parent("a", PrimitiveStrObject("value"))
    x = o.clone()

    assert o.map == x.map

    x.meta_remove_parent("a")

    assert o.map != x.map
    assert o != x
    assert "a" in o.parent_slot_keys


def test_meta_remove_parent():
    a_slot = PrimitiveStrObject("value a")
    b_slot = PrimitiveStrObject("value b")

    o = Object()
    o.meta_add_parent("a", a_slot)
    o.meta_add_parent("b", b_slot)

    assert "a" in o.parent_slot_keys
    assert "b" in o.parent_slot_keys

    assert o.meta_get_parent("a") is a_slot
    assert o.meta_get_parent("b") is b_slot

    o.meta_remove_parent("a")

    assert o.meta_get_parent("b") is b_slot
    assert len(o._parent_slot_values) == 1


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


def test_parent_lookup_from_parent_tree():
    """
    Based on real case.
    """
    value = PrimitiveStrObject("value")

    o1 = Object()
    o2 = Object()
    o3 = o2.clone()
    o4 = Object()
    o5 = Object()

    o1.scope_parent = o2

    o2.scope_parent = o3
    o2.meta_add_parent("*", o5)

    o3.scope_parent = o4
    o3.meta_add_parent("*", o5)

    o4.scope_parent = o5
    o4.meta_add_slot("value", value)

    assert o1.get_slot("value") is None
    assert o1.parent_lookup("value") is value


def slot_lookup():
    val = PrimitiveStrObject("it is xex!")
    flat = PrimitiveStrObject("it is flat")

    p = Object()
    p.meta_add_slot("xex", val)

    o = Object()
    o.meta_add_parent("p", p)
    o.meta_add_parent("p", flat)

    assert o.get_slot("xex") is None
    assert o.slot_lookup("xex")[1] is val
    assert o.slot_lookup("flat")[1] is flat


def test_slot_lookup_from_scope_parent():
    p = Object()
    val = PrimitiveStrObject("it is xex!")
    p.meta_add_slot("xex", val)

    o = Object()
    o.scope_parent = p

    assert o.get_slot("xex") is None
    assert o.slot_lookup("xex")[1] is val


def test_slot_lookup_from_scope_parent_and_then_parents():
    p = Object()
    val = PrimitiveStrObject("it is xex!")
    p.meta_add_slot("a", val)

    interobj = Object()
    interobj.scope_parent = p

    o = Object()
    o.scope_parent = Object()
    o.scope_parent.meta_add_parent("*", interobj)

    assert o.slot_lookup("a")[1] is val


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


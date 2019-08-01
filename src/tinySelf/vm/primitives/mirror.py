# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


def primitive_add_slot(interpreter, pseudo_self, parameters):
    assert isinstance(pseudo_self, Mirror)
    name = parameters[0]
    assert isinstance(name, PrimitiveStrObject)
    val = parameters[1]
    assert isinstance(val, Object)

    pseudo_self.obj_to_mirror.meta_add_slot(name.value, val)
    val.scope_parent = None  # old scope_parent is no longer valid

    return pseudo_self.obj_to_mirror


def primitive_list_slots(interpreter, pseudo_self, parameters):
    from tinySelf.vm.primitives.primitive_list import PrimitiveListObject
    assert isinstance(pseudo_self, Mirror)

    return PrimitiveListObject(
        [PrimitiveStrObject(x) for x in pseudo_self.obj_to_mirror.slot_keys]
    )


def primitive_add_parent(interpreter, pseudo_self, parameters):
    assert isinstance(pseudo_self, Mirror)
    name = parameters[0]
    assert isinstance(name, PrimitiveStrObject)
    val = parameters[1]
    assert isinstance(val, Object)

    pseudo_self.obj_to_mirror.meta_add_parent(name.value, val)

    return pseudo_self.obj_to_mirror


def primitive_list_parents(interpreter, pseudo_self, parameters):
    from tinySelf.vm.primitives.primitive_list import PrimitiveListObject
    assert isinstance(pseudo_self, Mirror)

    return PrimitiveListObject([
        PrimitiveStrObject(x)
        for x in pseudo_self.obj_to_mirror.parent_slot_keys
    ])


class Mirror(Object):
    def __init__(self, obj_to_mirror, obj_map=None):
        Object.__init__(self, obj_map)

        assert isinstance(obj_to_mirror, Object)
        self.obj_to_mirror = obj_to_mirror

        add_primitive_fn(self, "toSlot:Add:", primitive_add_slot, ["name", "obj"])
        add_primitive_fn(self, "toParent:Add:", primitive_add_parent, ["name", "obj"])
        add_primitive_fn(self, "listSlots", primitive_list_slots, [])
        add_primitive_fn(self, "listParents", primitive_list_parents, [])

    def __eq__(self, obj):
        if not isinstance(obj, Mirror):
            return False

        return self.obj_to_mirror is obj.obj_to_mirror

    def __str__(self):
        return "Mirror(%s)" % self.obj_to_mirror.__str__()

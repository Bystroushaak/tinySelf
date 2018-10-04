# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn


class PrimitiveNilObjectSingleton(Object):
    def __init__(self):
        Object.__init__(self)

    def __str__(self):
        return "PrimitiveNilObject()"


_NIL_OBJ = PrimitiveNilObjectSingleton()
def PrimitiveNilObject():
    return _NIL_OBJ


class AssignmentPrimitive(Object):
    def __init__(self, real_parent=None):
        self.real_parent = real_parent

    @property
    def is_assignment_primitive(self):
        return True

    @property
    def has_code(self):
        return False

    @property
    def has_primitive_code(self):
        return False

    def __str__(self):
        return "AssignmentPrimitive()"


def add_block_trait(block):
    obj = Object()
    obj.meta_add_slot("value", block)
    obj.meta_add_slot("with:", block)
    obj.meta_add_slot("with:With:", block)
    obj.meta_add_slot("with:With:With:", block)
    obj.meta_add_slot("with:With:With:With:", block)
    obj.meta_add_slot("withAll:", block)

    return obj


# def _primitive_create_mirror(obj):
#     def list_slots():
#         for slot_name in obj.map.slots.keys():
#             pass

#     mirror_obj = Object()
#     mirror_obj.meta_add_slot("mirroredObj", obj)


def get_primitives():
    """
    Return object with primitive functions mapped to its slots.

    Returns:
        obj: Instance of tinySelf's Object.
    """
    primitives = Object()

    # def create_primitive_int_instance(literal):
    #     return PrimitiveIntObject(literal)

    # add_primitive_fn(primitives, "primitiveInt", lambda x: PrimitiveIntObject(x), ["literal"])
    # add_primitive_fn(primitives, "primitiveStr", lambda x: PrimitiveStrObject(x), ["literal"])
    primitives.meta_add_slot("primitiveNil", PrimitiveNilObject())

    # _add_primitive(primitives, "mirrorOn:", _primitive_create_mirror, ["obj"])

    return primitives

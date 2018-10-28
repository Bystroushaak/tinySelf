# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.mirror import Mirror

from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject

from tinySelf.vm.primitives.primitive_nil import PrimitiveNilObject
from tinySelf.vm.primitives.primitive_true import PrimitiveTrueObject
from tinySelf.vm.primitives.primitive_false import PrimitiveFalseObject

from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_method


class AssignmentPrimitive(Object):
    def __init__(self, real_parent=None):
        Object.__init__(self)
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


class ErrorObject(Object):
    def __init__(self, message, process_stack):
        Object.__init__(self)
        self.message = message
        self.process_stack = process_stack

    @property
    def has_code(self):
        return False

    @property
    def has_primitive_code(self):
        return False

    def __str__(self):
        return "ErrorObject(%s)" % self.message


def add_block_trait(block):
    obj = Object()
    obj.meta_add_slot("value", block)
    obj.meta_add_slot("with:", block)
    obj.meta_add_slot("with:With:", block)
    obj.meta_add_slot("with:With:With:", block)
    obj.meta_add_slot("with:With:With:With:", block)
    obj.meta_add_slot("withAll:", block)

    return obj


def _create_mirror(_, __, parameters):
    obj = parameters[0]
    assert isinstance(obj, Object)

    return Mirror(obj)


def get_primitives():
    """
    Return object with primitive functions mapped to its slots.

    Returns:
        obj: Instance of tinySelf's Object.
    """
    primitives = Object()

    # add_primitive_fn(primitives, "primitiveInt", lambda x: PrimitiveIntObject(x), ["literal"])
    # add_primitive_fn(primitives, "primitiveStr", lambda x: PrimitiveStrObject(x), ["literal"])
    primitives.meta_add_slot("nil", PrimitiveNilObject())
    primitives.meta_add_slot("true", PrimitiveTrueObject())
    primitives.meta_add_slot("false", PrimitiveFalseObject())

    add_primitive_fn(primitives, "mirrorOn:", _create_mirror, ["obj"])

    return primitives

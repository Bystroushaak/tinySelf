# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.mirror import Mirror

from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject

from tinySelf.vm.primitives.primitive_float import FLOAT_TRAIT
from tinySelf.vm.primitives.primitive_float import PrimitiveFloatObject

from tinySelf.vm.primitives.primitive_nil import PrimitiveNilObject
from tinySelf.vm.primitives.primitive_true import PrimitiveTrueObject
from tinySelf.vm.primitives.primitive_false import PrimitiveFalseObject
from tinySelf.vm.primitives.primitive_list import PrimitiveListObject
from tinySelf.vm.primitives.primitive_dict import ObjectDict
from tinySelf.vm.primitives.primitive_dict import PrimitiveDictObject

from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn

from tinySelf.vm.primitives.interpreter_primitives import ErrorObject
from tinySelf.vm.primitives.interpreter_primitives import gen_interpreter_primitives

from tinySelf.vm.primitives.os import get_primitive_os

from tinySelf.vm.primitives.primitive_time import get_primitive_time_object

from tinySelf.vm.primitives.block_traits import add_block_trait
from tinySelf.vm.primitives.block_traits import _USER_EDITABLE_BLOCK_TRAIT


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


def _create_mirror(interpreter, self, parameters):
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

    primitives.meta_add_slot("nil", PrimitiveNilObject())
    primitives.meta_add_slot("true", PrimitiveTrueObject())
    primitives.meta_add_slot("false", PrimitiveFalseObject())
    primitives.meta_add_slot("list", PrimitiveListObject([]))
    primitives.meta_add_slot("dict", PrimitiveDictObject(ObjectDict.copy()))

    traits = Object()
    primitives.meta_add_slot("traits", traits)
    traits.meta_add_slot("block", _USER_EDITABLE_BLOCK_TRAIT)
    traits.meta_add_slot("float", FLOAT_TRAIT)

    primitives.meta_add_slot("os", get_primitive_os())
    primitives.meta_add_slot("time", get_primitive_time_object())

    add_primitive_fn(primitives, "mirrorOn:", _create_mirror, ["obj"])

    return primitives

# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.mirror import Mirror

from tinySelf.vm.primitives.primitive_int import PrimitiveIntObject
from tinySelf.vm.primitives.primitive_str import PrimitiveStrObject
from tinySelf.vm.primitives.primitive_float import PrimitiveFloatObject

from tinySelf.vm.primitives.primitive_nil import PrimitiveNilObject
from tinySelf.vm.primitives.primitive_true import PrimitiveTrueObject
from tinySelf.vm.primitives.primitive_false import PrimitiveFalseObject
from tinySelf.vm.primitives.primitive_list import PrimitiveListObject

from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_method

from tinySelf.vm.primitives.interpreter_primitives import ErrorObject
from tinySelf.vm.primitives.interpreter_primitives import gen_interpreter_primitives

from tinySelf.vm.primitives.primitive_time import get_primitive_time_object


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


class BlockTrait(Object):
    pass


_USER_EDITABLE_BLOCK_TRAIT = BlockTrait()


def _print_block_source(context, block_obj, parameters):
    ast = block_obj.get_slot("value").ast
    return PrimitiveStrObject(ast.source_pos.source_snippet)


def _get_lineno(context, block_obj, parameters):
    ast = block_obj.get_slot("value").ast
    return PrimitiveIntObject(ast.source_pos.start_line)


def _create_block_trait_prototype():
    obj = Object()

    placer = PrimitiveNilObject()

    obj.meta_add_slot("value", placer, check_duplicates=True)
    obj.meta_add_slot("with:", placer, check_duplicates=True)
    obj.meta_add_slot("with:With:", placer, check_duplicates=True)
    obj.meta_add_slot("with:With:With:", placer, check_duplicates=True)
    obj.meta_add_slot("with:With:With:With:", placer, check_duplicates=True)
    obj.meta_add_slot("withAll:", placer, check_duplicates=True)

    add_primitive_fn(obj, "asString", _print_block_source, [])
    add_primitive_fn(obj, "getLineNumber", _get_lineno, [])

    obj.scope_parent = _USER_EDITABLE_BLOCK_TRAIT

    return obj


_BLOCK_TRAIT_PROTOTYPE = _create_block_trait_prototype()


def add_block_trait(block):
    obj = _BLOCK_TRAIT_PROTOTYPE.clone()
    obj.set_slot("value", block)

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
    primitives.meta_add_slot("block_traits", _USER_EDITABLE_BLOCK_TRAIT)
    primitives.meta_add_slot("list", PrimitiveListObject([]))

    primitives.meta_add_slot("time", get_primitive_time_object())

    add_primitive_fn(primitives, "mirrorOn:", _create_mirror, ["obj"])

    return primitives

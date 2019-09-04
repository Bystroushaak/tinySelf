# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveStrObject
from tinySelf.vm.primitives import add_primitive_fn


class BlockTraitSingleton(Object):
    pass


_USER_EDITABLE_BLOCK_TRAIT = BlockTraitSingleton()


def BlockTrait():
    return _USER_EDITABLE_BLOCK_TRAIT


def _print_block_source(interpreter, block_obj, parameters):
    ast = block_obj.get_slot("value").ast

    if ast is not None:
        return PrimitiveStrObject(ast.source_pos.source_snippet)

    return PrimitiveStrObject(block_obj.__str__())


def _get_lineno(interpreter, block_obj, parameters):
    ast = block_obj.get_slot("value").ast
    return PrimitiveIntObject(ast.source_pos.start_line)


def add_block_trait(block):
    obj = Object()
    obj.meta_add_slot("value", block)
    obj.meta_add_slot("with:", block)
    obj.meta_add_slot("with:With:", block)
    obj.meta_add_slot("with:With:With:", block)
    obj.meta_add_slot("with:With:With:With:", block)
    obj.meta_add_slot("withAll:", block)

    # obj.meta_add_parent("trait", BlockTrait())
    add_primitive_fn(obj, "asString", _print_block_source, [])
    add_primitive_fn(obj, "getLineNumber", _get_lineno, [])

    obj.scope_parent = BlockTrait()

    return obj

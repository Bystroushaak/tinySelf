# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object


def build_primitive_code_obj(primitive_fn, arguments):
    code_obj = Object()

    code_obj.map.arguments = arguments
    code_obj.map.primitive_code = primitive_fn

    return code_obj


def add_primitive_fn(obj, slot_name, primitive_fn, arguments):
    assert isinstance(obj, Object)
    assert isinstance(slot_name, str)
    assert isinstance(arguments, list)

    primitive_code_obj = build_primitive_code_obj(primitive_fn, arguments)
    obj.meta_add_slot(slot_name, primitive_code_obj)

# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object


def _build_primitive(arguments, primitive_fn):
    code_obj = Object()

    code_obj.map.arguments = arguments
    code_obj.primitive_code = primitive_fn

    return code_obj


def _primitive_create_mirror(obj):
    pass


def get_primitives():
    primitives = Object()
    primitives.set_slot("mirror:", _primitive_create_mirror)
    primitives.arguments.append("obj")

    return primitives

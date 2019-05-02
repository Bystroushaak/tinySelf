# -*- coding: utf-8 -*-
from tinySelf.parser import lex_and_parse
from tinySelf.vm.object_layout import Object


def build_primitive_code_obj(primitive_fn, arguments):
    code_obj = Object()

    code_obj.map.arguments = arguments
    code_obj.map.primitive_code = primitive_fn

    return code_obj


def add_primitive_fn(obj, slot_name, primitive_fn, arguments):
    """
    Into the `obj` insert at `slot_name` `primitive_fn` expecting `arguments`.

    `primitive_fn` is expected to be rpython function with exactly three
    arguments:

        - interpreter (interpreter instance)
        - receiver (object into which is this fn bound)
        - parameters (list of parameters)

    Args:
        obj (Object): Instance of Object.
        slot_name (str): Name of the slot where the `primitive_fn` will be bound.
        primitive_fn (fn): RPython function which will be called.
        arguments (list): List of strings with named parameters.

    Returns:
        Object: Code object with bound `primitive_fn`.
    """
    assert isinstance(obj, Object)
    assert isinstance(slot_name, str)
    assert isinstance(arguments, list)

    primitive_code_obj = build_primitive_code_obj(primitive_fn, arguments)
    obj.meta_add_slot(slot_name, primitive_code_obj)

    return primitive_code_obj


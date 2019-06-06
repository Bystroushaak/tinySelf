# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn

from tinySelf.vm.primitives.os.primitive_files import get_primitive_files


def get_primitive_os():
    os_obj = Object()
    add_primitive_fn(os_obj, "files", get_primitive_files(), [])

    return os_obj

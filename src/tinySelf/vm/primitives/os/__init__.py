# -*- coding: utf-8 -*-
from tinySelf.vm.object_layout import Object

from tinySelf.vm.primitives.os.primitive_files import get_primitive_files
from tinySelf.vm.primitives.os.primitive_socket import get_primitive_socket


def get_primitive_os():
    os_obj = Object()
    os_obj.meta_add_slot("files", get_primitive_files())
    os_obj.meta_add_slot("socket", get_primitive_socket())

    return os_obj

# -*- coding: utf-8 -*-
import time

from tinySelf.vm.object_layout import Object
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn
from tinySelf.vm.primitives.primitive_float import PrimitiveFloatObject


def get_timestamp(interpreter, time_obj, parameters):
    return PrimitiveFloatObject(time.time())


def get_primitive_time_object():
    time_obj = Object()
    add_primitive_fn(time_obj, "timestamp", get_timestamp, [])

    return time_obj

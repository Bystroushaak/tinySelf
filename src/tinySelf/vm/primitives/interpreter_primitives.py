# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_method

from tinySelf.vm.object_layout import Object


NIL = PrimitiveNilObject()


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


def primitive_get_number_of_processes(interpreter, _, parameters):
    return PrimitiveIntObject(len(interpreter.processes))


def primitive_get_number_of_stack_frames(interpreter, _, parameters):
    return PrimitiveIntObject(len(interpreter.process.frames))


def primitive_set_error_handler(interpreter, _, parameters):
    blck = parameters[0]
    assert isinstance(blck, Object)

    interpreter.process.frame.error_handler = blck

    return NIL


def _get_frame_with_error_handler(frames):
    while frames:
        frame = frames.pop()
        if frame.error_handler is not None:
            frames.append(frame)
            return frame

    return None


def primitive_halt(interpreter, _, parameters):
    obj = parameters[0]
    assert isinstance(obj, Object)

    process = interpreter.remove_active_process()

    if interpreter.process_count == 0:
        interpreter.process = process

    process.result = obj
    process.finished = True
    process.finished_with_error = False

    return obj


def primitive_restore_process_with(interpreter, _, parameters):
    obj = parameters[0]
    assert isinstance(obj, Object)
    with_obj = parameters[1]
    assert isinstance(with_obj, Object)

    if not isinstance(obj, ErrorObject):
        raise ValueError("This is not instance of error object!")

    obj.process_stack.frame.push(with_obj)
    interpreter.restore_process(obj.process_stack)

    return None


def primitive_raise_error(interpreter, _, parameters):
    msg = parameters[0]
    assert isinstance(msg, Object)

    poped_frames = interpreter.process.frames[:]
    frame_with_handler = _get_frame_with_error_handler(poped_frames)
    process = interpreter.remove_active_process()

    if frame_with_handler is None:
        process.result = msg
        process.finished = True
        process.finished_with_error = True

        if interpreter.process_count == 0:
            interpreter.process = process

        return None

    error_handler = frame_with_handler.error_handler.get_slot("with:With:")
    if error_handler is None:
        raise ValueError("Error handler must react to with:With: message!")

    new_code_context = error_handler.code_context
    error_handler.scope_parent = interpreter._create_intermediate_params_obj(
        error_handler.scope_parent,
        error_handler,
        [msg, ErrorObject(msg, process)]
    )
    new_code_context.self = error_handler.scope_parent

    interpreter.add_process(new_code_context)

    return None


def gen_interpreter_primitives(interpreter):
    interpreter_namespace = Object()

    add_primitive_method(interpreter, interpreter_namespace, "numberOfProcesses",
                         primitive_get_number_of_processes, [])
    add_primitive_method(interpreter, interpreter_namespace, "numberOfFrames",
                         primitive_get_number_of_stack_frames, [])
    add_primitive_method(interpreter, interpreter_namespace, "setErrorHandler:",
                         primitive_set_error_handler, ["blck"])
    add_primitive_method(interpreter, interpreter_namespace, "error:",
                         primitive_raise_error, ["obj"])
    add_primitive_method(interpreter, interpreter_namespace, "halt:",
                         primitive_halt, ["obj"])
    add_primitive_method(interpreter, interpreter_namespace, "restoreProcess:With:",
                         primitive_restore_process_with, ["msg", "err_obj"])

    return interpreter_namespace

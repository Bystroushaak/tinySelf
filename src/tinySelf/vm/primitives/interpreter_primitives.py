# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveStrObject
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_method

from tinySelf.vm.object_layout import Object

from tinySelf.vm.code_context import CodeContext

from tinySelf.parser import lex_and_parse_as_root


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


def _get_number_of_processes(interpreter, _, parameters):
    return PrimitiveIntObject(len(interpreter.processes))


def _get_number_of_stack_frames(interpreter, _, parameters):
    return PrimitiveIntObject(len(interpreter.process.frames))


def _set_error_handler(interpreter, _, parameters):
    blck = parameters[0]
    assert isinstance(blck, Object)

    interpreter.process.frame.error_handler = blck

    return NIL


def _get_frame_with_error_handler(frames):
    shallow_copy = frames[:]

    while shallow_copy:
        frame = shallow_copy.pop()
        if frame.error_handler is not None:
            shallow_copy.append(frame)
            return frame

    return None


def _halt(interpreter, _, parameters):
    obj = parameters[0]
    assert isinstance(obj, Object)

    process = interpreter.remove_active_process()

    if interpreter.process_count == 0:
        interpreter.process = process

    process.result = obj
    process.finished = True
    process.finished_with_error = False

    return obj


def _restore_process_with(interpreter, _, parameters):
    obj = parameters[0]
    assert isinstance(obj, Object)
    with_obj = parameters[1]
    assert isinstance(with_obj, Object)

    if not isinstance(obj, ErrorObject):
        raise ValueError("This is not instance of error object!")

    obj.process_stack.frame.push(with_obj)
    interpreter.restore_process(obj.process_stack)

    return None


def _raise_error(interpreter, _, parameters):
    msg = parameters[0]
    assert isinstance(msg, Object)

    poped_frames = interpreter.process.frames
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
        [msg, ErrorObject(msg, process)]  # process is passed to the error_handler
    )
    new_code_context.self = error_handler.scope_parent

    interpreter.add_process(new_code_context)

    return None


def _run_script(interpreter, scope_parent, parameters):
    path = parameters[0]
    assert isinstance(path, Object)

    if not isinstance(path, PrimitiveStrObject):
        return _raise_error(
            interpreter,
            scope_parent,
            [PrimitiveStrObject("runScript: str parameter expected")]
        )

    try:
        with open(path.value) as f:
            source = f.read()
    except Exception as e:
        return _raise_error(
            interpreter,
            scope_parent,
            [PrimitiveStrObject("runScript: %s" % str(e))]
        )

    ast_root = lex_and_parse_as_root(source)

    if not ast_root.ast:
        return

    code = ast_root.compile(CodeContext())
    code.finalize()

    method_obj = Object()
    method_obj.code_context = code
    code.self = scope_parent

    interpreter._push_code_obj_for_interpretation(
        next_bytecode=0,  # disable TCO
        scope_parent=scope_parent,
        method_obj=method_obj,
        parameters=[],
    )


def gen_interpreter_primitives(interpreter):
    interpreter_namespace = Object()

    add_primitive_method(interpreter, interpreter_namespace, "numberOfProcesses",
                         _get_number_of_processes, [])
    add_primitive_method(interpreter, interpreter_namespace, "numberOfFrames",
                         _get_number_of_stack_frames, [])
    add_primitive_method(interpreter, interpreter_namespace, "setErrorHandler:",
                         _set_error_handler, ["blck"])
    add_primitive_method(interpreter, interpreter_namespace, "error:",
                         _raise_error, ["obj"])
    add_primitive_method(interpreter, interpreter_namespace, "halt:",
                         _halt, ["obj"])
    add_primitive_method(interpreter, interpreter_namespace, "restoreProcess:With:",
                         _restore_process_with, ["msg", "err_obj"])
    add_primitive_method(interpreter, interpreter_namespace, "runScript:",
                         _run_script, ["path"])

    return interpreter_namespace

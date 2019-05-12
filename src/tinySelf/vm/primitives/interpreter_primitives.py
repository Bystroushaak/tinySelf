# -*- coding: utf-8 -*-
from tinySelf.vm.primitives import PrimitiveStrObject
from tinySelf.vm.primitives import PrimitiveIntObject
from tinySelf.vm.primitives import PrimitiveNilObject
from tinySelf.vm.primitives.add_primitive_fn import add_primitive_fn

from tinySelf.vm.object_layout import Object

from tinySelf.vm.code_context import CodeContext

from tinySelf.parser import lex_and_parse
from tinySelf.parser import lex_and_parse_as_root
from tinySelf.parser.ast_tokens import Object as AstObject


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


def _get_number_of_processes(interpreter, self, parameters):
    return PrimitiveIntObject(len(interpreter.processes))


def _get_number_of_stack_frames(interpreter, self, parameters):
    return PrimitiveIntObject(interpreter.process.length)


def _set_error_handler(interpreter, self, parameters):
    blck = parameters[0]
    assert isinstance(blck, Object)

    interpreter.process.frame.error_handler = blck

    return NIL


def _get_frame_with_error_handler(frame_linked_list):
    if frame_linked_list is None:
        return None

    while frame_linked_list is not None:
        if frame_linked_list.error_handler is not None:
            return frame_linked_list

        frame_linked_list = frame_linked_list.prev_stack

    return None


def _halt(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(obj, Object)

    process = interpreter.remove_active_process()

    if interpreter.process_count == 0:
        interpreter.process = process

    process.result = obj
    process.finished = True
    process.finished_with_error = False

    return obj


def _restore_process_with(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(obj, Object)
    with_obj = parameters[1]
    assert isinstance(with_obj, Object)

    if not isinstance(obj, ErrorObject):
        raise ValueError("This is not instance of error object!")

    obj.process_stack.frame.push(with_obj)
    interpreter.restore_process(obj.process_stack)

    return None


def _restore_process(interpreter, self, parameters):
    obj = parameters[0]
    assert isinstance(obj, Object)

    if not isinstance(obj, ErrorObject):
        raise ValueError("This is not instance of error object!")

    obj.process_stack.push_frame(CodeContext(), NIL)  # it is immediatelly poped anyway
    interpreter.restore_process(obj.process_stack)

    return None


def _raise_error(interpreter, self, parameters):
    msg = parameters[0]
    assert isinstance(msg, Object)

    frame_with_handler = _get_frame_with_error_handler(interpreter.process.frame)
    process = interpreter.remove_active_process()

    if frame_with_handler is None:
        process.result = msg
        process.finished = True
        process.finished_with_error = True

        return None

    error_handler = frame_with_handler.error_handler.get_slot("with:With:")
    if error_handler is None:
        raise ValueError("Error handler must react to with:With: message!")

    error_handler.scope_parent = interpreter._create_intermediate_params_obj(
        error_handler.scope_parent,
        error_handler,
        [msg, ErrorObject(msg, process)]  # process is passed to the error_handler
    )

    process = interpreter.add_process(error_handler.code_context)
    process.frame.self = error_handler.scope_parent

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

    interpreter._push_code_obj_for_interpretation(
        next_bytecode=0,  # disable TCO
        scope_parent=scope_parent,
        method_obj=method_obj,
        parameters=[],
    )

    interpreter.process.frame.source_path = path.value


def call_tinyself_code_from_primitive(interpreter, code_str, code_parameters_values):
    assert isinstance(code_str, str)

    wrapping_obj = lex_and_parse(code_str)[0]
    assert isinstance(wrapping_obj, AstObject)

    code = wrapping_obj.compile()
    code.finalize()

    method_obj = Object()
    method_obj.map.ast = wrapping_obj
    method_obj.scope_parent = interpreter.process.frame.self

    # this may be a bit unintuitive, but whole surrounding object is compiled
    # and I want just the code object without slot pushing, which is the first
    # object literal in the compiled object
    method_obj.map.code_context = code.literals[0].value.code_context

    interpreter._push_code_obj_for_interpretation(
        next_bytecode=0,  # disable TCO
        scope_parent=interpreter.process.frame.self,
        method_obj=method_obj,
        parameters=code_parameters_values,
    )


def _eval_method_obj(interpreter, scope_parent, parameters):
    code = parameters[0]
    assert isinstance(code, PrimitiveStrObject)

    call_tinyself_code_from_primitive(interpreter, code.value, [])


def _get_script_path(interpreter, scope_parent, parameters):
    paths = [frame.source_path
             for frame in interpreter.process
             if frame.source_path]

    if not paths:
        return PrimitiveStrObject("")

    return PrimitiveStrObject(paths.pop())


def gen_interpreter_primitives(interpreter):
    interpreter_namespace = Object()

    add_primitive_fn(interpreter_namespace, "numberOfProcesses",
                     _get_number_of_processes, [])
    add_primitive_fn(interpreter_namespace, "numberOfFrames",
                     _get_number_of_stack_frames, [])
    add_primitive_fn(interpreter_namespace, "setErrorHandler:", _set_error_handler,
                     ["blck"])
    add_primitive_fn(interpreter_namespace, "error:", _raise_error, ["obj"])
    add_primitive_fn(interpreter_namespace, "halt:", _halt, ["obj"])
    add_primitive_fn(interpreter_namespace, "restoreProcess:", _restore_process,
                     ["err_obj"])
    add_primitive_fn(interpreter_namespace, "restoreProcess:With:",
                     _restore_process_with, ["msg", "err_obj"])
    add_primitive_fn(interpreter_namespace, "runScript:", _run_script, ["path"])
    add_primitive_fn(interpreter_namespace, "evalMethodObj:",
                     _eval_method_obj, ["code"])
    add_primitive_fn(interpreter_namespace, "scriptPath",
                     _get_script_path, [])

    return interpreter_namespace

# -*- coding: utf-8 -*-
from plantuml_composer import Root
from plantuml_composer import Object as PUObject
from plantuml_composer import Frame

from tinySelf.vm import Object


OBJ_MAP_COUNTER = 0
FRAMESET_COUNTER = 0


class ObjToPlantUML(object):
    def __init__(self, obj, recursive=False, _processed_ids=None):
        self.obj = obj
        self.recursive = recursive

        self._plantuml_repr = ""

        if _processed_ids is None:
            self._processed_ids = set()
        else:
            self._processed_ids = _processed_ids

    def _write(self, s):
        self._plantuml_repr += s

    def _writeln(self, s):
        self._write(s)
        self._write('\n')

    def _reset(self):
        self._plantuml_repr = ""
        self._processed_ids = set()

    def dump_to_file(self, file_handle):
        self._reset()

        file_handle.write("@startuml\n")

        plantuml_repr, connections = self._dump_obj_to_plantuml()
        file_handle.write(plantuml_repr)

        # conneections have to be written after the classes in order to use
        # customized names in plantuml
        for connection in connections:
            file_handle.write(connection)

        file_handle.write("@enduml\n")

    def _dump_obj_to_plantuml(self):
        """
        Dump information about object to plantuml.

        Returns:
            tuple[str, list]: Description of all objects, list of all relations.
        """
        if self.obj.id in self._processed_ids:
            return '', []
        else:
            self._processed_ids.add(self.obj.id)

        name = self.obj.__class__.__name__
        self._writeln('class %s as "%s (id: %s)" {' % (self.obj.id, name, self.obj.id))

        self._dump_parameters()
        objects_to_process = []
        objects_to_process.extend(self._dump_parents())
        objects_to_process.extend(self._dump_slots())
        self._dump_ast()

        self._writeln('}')

        relations = []
        for is_parent, obj_name, other_obj in objects_to_process:
            obj_dumper = ObjToPlantUML(other_obj, self.recursive, self._processed_ids)
            obj_repr, obj_links = obj_dumper._dump_obj_to_plantuml()

            self._writeln(obj_repr)
            obj_type = "parent" if is_parent else "slot"
            line_type = "-->" if is_parent else "..>"

            relations.append('%s %s %s: %s %s\n' % (self.obj.id, line_type, other_obj.id, obj_type, obj_name))
            relations.extend(obj_links)

        if self.obj.scope_parent:
            relations.append('%s --> %s: scope_parent\n' % (self.obj.id, self.obj.scope_parent.id))

            obj_dumper = ObjToPlantUML(self.obj.scope_parent, self.recursive, self._processed_ids)
            scope_parent_repr, links = obj_dumper._dump_obj_to_plantuml()
            self._writeln(scope_parent_repr)
            relations.extend(links)

        return self._plantuml_repr, relations

    def _dump_parents(self):
        if self.obj._parent_slot_values is None:
            return

        self._writeln('  -- parents: --')

        if self.obj.scope_parent:
            self._writeln('  scope_parent = id(%s)' % self.obj.scope_parent.id)

        for parent_name, parent in zip(self.obj.map._parent_slots.keys(), self.obj._parent_slot_values):
            self._writeln('  ""%s*"" = id(%s)' % (parent_name, parent.id))
            yield [True, parent_name, parent]

    def _dump_slots(self):
        if self.obj._slot_values is None:
            return

        self._writeln('  -- slots: --')
        for slot_name, slot in zip(self.obj.slot_keys, self.obj._slot_values):
            self._writeln('  ""%s"" = id(%s)' % (slot_name, slot.id))

            if self.recursive:
                yield [False, slot_name, slot]

    def _dump_ast(self):
        if self.obj.ast is None or not self.obj.ast.source_pos.source_snippet:
            return

        self._writeln('  -- source: --')

        # creole pre-formatted text line by line; ugly, but only way I was able to make work
        for line in self.obj.ast.source_pos.source_snippet.splitlines():
            self._writeln('  ""%s""' % line)

    def _dump_parameters(self):
        if not self.obj.parameters:
            return

        self._writeln('  -- parameters: --')
        for parameter in self.obj.parameters:
            self._writeln('  ' + parameter)  # TODO: plantuml escaping


def obj_map_to_plantuml(obj, number_files=False, recursive=False, prefix="obj_parent_map"):
    if number_files:
        global OBJ_MAP_COUNTER
        filename = "%s_%d.plantuml" % (prefix, OBJ_MAP_COUNTER)
        OBJ_MAP_COUNTER += 1
    else:
        filename = "%s.plantuml" % prefix

    obj_dumper = ObjToPlantUML(obj, recursive)
    with open(filename, "w") as f:
        obj_dumper.dump_to_file(f)


def _render_object(obj, name=None):
    if obj is None:
        return PUObject("None")

    if not name:
        name = str(id(obj))

    o = PUObject(name)
    o.add_property("__class__: " + obj.__class__.__name__)
    o.add_property("scope_parent: %s" % id(obj.scope_parent))

    if obj.is_block:
        o.add_property("Block")

    if obj.map._parent_slots:
        o.add_property("---")
        o.add_property("Parents:")
        for key, val in obj.map._parent_slots.iteritems():
            o.add_property("%s: %s" % (key, id(val)))

    if obj.slot_keys:
        o.add_property("---")
        o.add_property("Slots:")
        for slot_name in obj.slot_keys:
            o.add_property("%s: %s" % (slot_name, id(obj.get_slot(slot_name))))

    return o


def _render_method_stack(cnt, method_stack):
    f = Frame(name=str(cnt))

    settings = PUObject("settings%s" % cnt, "settings", prop=[
        "bc_index = %d" % method_stack.bc_index,
        "code_context = %s" % method_stack.code_context,
        # "code_context.self = %s" % method_stack.code_context.self,
        "error_handler = %s" % method_stack.error_handler,
    ])

    self_obj = _render_object(method_stack.self)
    f.add(self_obj)
    settings.connect(self_obj, pos="r", desc=".code_context.self")

    prev = settings
    for i, obj in enumerate(method_stack):
        plantuml_obj = _render_object(obj, name="%s_%s_%s" % (id(obj), cnt, i))

        f.add(plantuml_obj)
        if prev:
            prev.connect(plantuml_obj)

        prev = plantuml_obj

    f.add(settings)

    return f


def process_stack_to_plantuml(process, numbered=False, prefix="frame"):
    ps = Frame(name="process_stack")

    settings = PUObject("settings")
    settings.add_property("result: %s" % process.result)
    settings.add_property("finished: %s" % process.finished)
    settings.add_property("finished_with_error: %s" % process.finished_with_error)
    ps.add(settings)

    def iterate_frames(process):
        frame = process.frame

        while frame:
            yield frame
            frame = frame.prev_stack

    prev = None
    for cnt, frame in enumerate(reversed(list(iterate_frames(process)))):
        plantuml_frame = _render_method_stack(cnt, frame)
        ps.add(plantuml_frame)

        if prev:
            prev.connect(plantuml_frame)

        prev = plantuml_frame

    obj_map_to_plantuml(process.frame.self)

    if numbered:
        global FRAMESET_COUNTER
        fn = "%s_%d.plantuml" % (prefix, FRAMESET_COUNTER)
        FRAMESET_COUNTER += 1
    else:
        fn = "%s.plantuml" % prefix

    with open(fn, "w") as f:
        f.write(Root([ps]).to_str())


if __name__ == '__main__':
    from tinySelf.vm.frames import MethodStack
    from tinySelf.vm.frames import ProcessStack

    p = ProcessStack()
    process_stack_to_plantuml(p)

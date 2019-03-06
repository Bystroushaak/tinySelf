# -*- coding: utf-8 -*-
from plantuml_composer import Root
from plantuml_composer import Class
from plantuml_composer import Object
from plantuml_composer import Frame


OBJ_MAP_COUNTER = 0
FRAMESET_COUNTER = 0


def dump_obj_to_plantuml(f, o):
    f.write('class %s as "%s (%s)" {\n' % (id(o), id(o), o.__class__.__name__))

    if o:
        for key in o.slot_keys:
            f.write("    %s (%s)\n" % (key, id(o.get_slot(key))))

    f.write("}\n")

    if o is None:
        return None, {}

    return o.scope_parent, o.expensive_parent_slots


def _get_object_graph(obj):
    objs_to_print = []

    objs = [obj]
    while objs:
        o = objs.pop(0)

        if o in objs_to_print:
            continue

        objs_to_print.append(o)
        if o is None:
            continue

        objs.append(o.scope_parent)
        objs.extend(o._parent_slot_values)

    return objs_to_print


def obj_map_to_plantuml(obj, numbered=False, print_depth=False, prefix="parent_map"):
    if numbered:
        global OBJ_MAP_COUNTER
        f = open("%s_%d.plantuml" % (prefix, OBJ_MAP_COUNTER), "w")
        OBJ_MAP_COUNTER += 1
    else:
        f = open("%s.plantuml" % prefix, "w")

    f.write("@startuml\n")

    objs_to_print = _get_object_graph(obj)

    connections = []
    for o in objs_to_print:
        sp, parents = dump_obj_to_plantuml(f, o)

        connections.append("%s --> %s: scope_parent\n" % (id(o), id(sp)))
        for key, val in parents.iteritems():
            connections.append("%s --> %s: parent %s\n" % (id(o), id(val), key))

    # conneections have to be written after the classes in order to use
    # customized names in plantuml
    for connection in connections:
        f.write(connection)

    f.write("@enduml\n")
    f.close()

    if print_depth:
        print
        print "depth", len(objs_to_print)
        print


def _render_object(obj, name=None):
    if obj is None:
        return Object("None")

    if not name:
        name = str(id(obj))

    o = Object(name)
    o.add_property("__class__: " + obj.__class__.__name__)
    o.add_property("scope_parent: %s" % id(obj.scope_parent))

    if obj.is_block:
        o.add_property("Block")

    if obj.map._parent_slots:
        o.add_property("---")
        o.add_property("Parents:")
        for key, val in obj.map._parent_slots.items():
            o.add_property("%s: %s" % (key, id(val)))

    if obj.slot_keys:
        o.add_property("---")
        o.add_property("Slots:")
        for slot_name in obj.slot_keys:
            o.add_property("%s: %s" % (slot_name, id(obj.get_slot(slot_name))))

    return o


def _render_method_stack(cnt, method_stack):
    f = Frame(name=str(cnt))

    settings = Object("settings%s" % cnt, "settings", prop=[
        "bc_index = %d" % method_stack.bc_index,
        "code_context = %s" % method_stack.code_context,
        # "code_context.self = %s" % method_stack.code_context.self,
        "error_handler = %s" % method_stack.error_handler,
        "tmp_method_obj_reference = %s" % method_stack.tmp_method_obj_reference,
    ])

    self_obj = _render_object(method_stack.self)
    f.add(self_obj)
    settings.connect(self_obj, pos="r", desc=".code_context.self")

    prev = settings
    for i, obj in enumerate(method_stack.stack):
        plantuml_obj = _render_object(obj, name="%s_%s_%s" % (id(obj), cnt, i))

        f.add(plantuml_obj)
        if prev:
            prev.connect(plantuml_obj)

        prev = plantuml_obj

    f.add(settings)

    return f


def process_stack_to_plantuml(process, numbered=False, prefix="frame"):
    ps = Frame(name="process_stack")

    settings = Object("settings")
    settings.add_property("result: %s" % process.result)
    settings.add_property("finished: %s" % process.finished)
    settings.add_property("finished_with_error: %s" % process.finished_with_error)
    ps.add(settings)

    prev = None
    for cnt, frame in enumerate(process.frames):
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
    from frames import MethodStack
    from frames import ProcessStack

    p = ProcessStack()
    process_stack_to_plantuml(p)

# -*- coding: utf-8 -*-
from collections import OrderedDict

from rply.token import BaseBox

from tinySelf.vm.bytecodes import *
from tinySelf.vm.code_context import CodeContext
from tinySelf.vm.object_layout import Object as ObjectRepresentation


def _repr_list_of_baseboxes(l):
    results = []
    for x in l:
        assert isinstance(x, BaseBox)
        results.append(x.__str__())

    return "[" + ", ".join(results) + "]"


def _repr_list_of_strs(l):
    results = []
    for x in l:
        assert isinstance(x, str)
        results.append(x)

    return "[" + ", ".join(results) + "]"


def _repr_dict(d):
    results = []
    for k, v in d.iteritems():
        assert isinstance(k, str)
        assert isinstance(v, BaseBox)
        results.append("%s: %s" % (k, v.__str__()))

    return "{" + ", ".join(results) + "}"


class SourcePos(BaseBox):
    def __init__(self, start_line, start_column, end_line, end_column, source=""):
        self.start_line = start_line
        self.start_column = start_column
        self.end_line = end_line
        self.end_column = end_column

        self.source_snippet = self._parse_source(source)

    def _parse_source(self, source):
        source_lines = source.splitlines()

        if self.start_line == self.end_line:
            line = source_lines[self.start_line - 1]
            return line[self.start_column-1:self.end_column].strip()

        relevant_lines = []
        for i in range(self.start_line, self.end_line):
            line = source_lines[i - 1]

            if i == self.start_line:
                relevant_lines.append(line[self.start_column:])
            elif i == self.end_line:
                relevant_lines.append(line[:self.end_line - 1])
            else:
                relevant_lines.append(line)

        return "\n".join(relevant_lines)


class Root(BaseBox):
    def __init__(self, tree=[]):
        self.ast = tree

    def compile(self, context):
        for item in self.ast:
            item.compile(context)

        return context

    def __str__(self):
        return "\n".join([x.__str__() for x in self.ast])


class Self(BaseBox):
    def compile(self, context):
        context.add_bytecode(BYTECODE_PUSH_SELF)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__)

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "Self()"


class Nil(Self):
    def compile(self, context):
        context.add_bytecode(BYTECODE_PUSH_LITERAL)
        context.add_bytecode(LITERAL_TYPE_NIL)
        context.add_bytecode(0)

        return context

    def __str__(self):
        return "Nil()"


class Object(BaseBox):
    def __init__(self, slots=None, params=None, code=None, parents=None,
                 source_pos=None):
        self.slots = OrderedDict()
        self.params = []
        self.code = []
        self.parents = OrderedDict()
        self.source_pos = source_pos

        if slots is not None:
            self.slots.update(slots)
        if params is not None:
            self.params.extend(params)
        if code is not None:
            self.code.extend(code)
        if parents is not None:
            self.parents.update(parents)

    def _add_slot_to_bytecode(self, context, name, value):
        boxed_name = String(name)
        boxed_name.compile(context)

        value.compile(context)

        context.add_bytecode(BYTECODE_ADD_SLOT)

    def compile(self, context):
        obj = ObjectRepresentation()
        obj.meta_set_ast(self)
        obj.meta_set_parameters(self.params)

        index = context.add_literal_obj(obj)
        context.add_bytecode(BYTECODE_PUSH_LITERAL)
        context.add_bytecode(LITERAL_TYPE_OBJ)
        context.add_bytecode(index)

        for name, value in self.slots.iteritems():
            self._add_slot_to_bytecode(context, name, value)
            context.add_bytecode(SLOT_NORMAL)

        for name, value in self.parents.iteritems():
            self._add_slot_to_bytecode(context, name, value)
            context.add_bytecode(SLOT_PARENT)

        if self.code:
            new_context = CodeContext()
            obj.meta_set_code_context(new_context)
            for item in self.code:
                item.compile(new_context)

            obj.map.code_context = new_context

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.slots == obj.slots and \
               self.params == obj.params and \
               self.code == obj.code and \
               self.parents == obj.parents

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        parameters = []

        if self.slots:
            parameters.append("slots=" + _repr_dict(self.slots))
        if self.params:
            assert isinstance(self.params[0], str)
            parameters.append("params=" + _repr_list_of_strs(self.params))
        if self.code:
            assert isinstance(self.code[0], BaseBox)
            parameters.append("code=" + _repr_list_of_baseboxes(self.code))
        if self.parents:
            parameters.append("parents=" + _repr_dict(self.parents))

        return "%s(%s)" % (self.__class__.__name__, ", ".join(parameters))


class Block(Object):
    def compile(self, context):
        block = ObjectRepresentation()
        block.meta_set_ast(self)
        block.meta_set_parameters(self.params)

        # push current scope
        context.add_bytecode(BYTECODE_PUSH_SELF)

        index = context.add_literal_obj(block)
        context.add_bytecode(BYTECODE_PUSH_LITERAL)
        context.add_bytecode(LITERAL_TYPE_BLOCK)
        context.add_bytecode(index)

        for name, value in self.slots.iteritems():
            self._add_slot_to_bytecode(context, name, value)
            context.add_bytecode(SLOT_NORMAL)

        for name, value in self.parents.iteritems():
            self._add_slot_to_bytecode(context, name, value)
            context.add_bytecode(SLOT_PARENT)

        new_context = CodeContext()
        block.meta_set_code_context(new_context)
        for item in self.code:
            item.compile(new_context)

        block.map.code_context = new_context

        return context


class IntNumber(BaseBox):
    def __init__(self, value):
        self.value = value

    def compile(self, context):
        index = context.add_literal_int(self.value)

        context.add_bytecode(BYTECODE_PUSH_LITERAL)
        context.add_bytecode(LITERAL_TYPE_INT)
        context.add_bytecode(index)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.value == obj.value

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "IntNumber(%s)" % self.value


class FloatNumber(BaseBox):
    def __init__(self, value):
        self.value = value

    def compile(self, context):
        index = context.add_literal_float(self.value)

        context.add_bytecode(BYTECODE_PUSH_LITERAL)
        context.add_bytecode(LITERAL_TYPE_FLOAT)
        context.add_bytecode(index)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.value == obj.value

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "FloatNumber(%s)" % self.value


def _escape_sequences(inp):
    if len(inp) < 2:
        return inp

    out = ""
    last = inp[0]
    inp = inp[1:] + "-"

    escape = last == "\\"
    for c in inp:
        if escape:
            if c == "n":
                last = "\n"
            elif c == "t":
                last = "\t"
            else:
                last = c

        out += last

        last = "" if escape else c
        escape = not escape if c == "\\" else False

    return out


class String(BaseBox):  # TODO: remove?
    def __init__(self, value):
        self.value = _escape_sequences(value)

    def compile(self, context):
        index = context.add_literal_str(self.value)

        context.add_bytecode(BYTECODE_PUSH_LITERAL)
        context.add_bytecode(LITERAL_TYPE_STR)
        context.add_bytecode(index)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.value == obj.value

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "'%s'" % self.value  # TODO: escaping


class MessageBase(BaseBox):
    def __init__(self, name):
        self.true_name = name

        self.name = name
        self.parent_name = ""

        if self.is_resend:
            self.parent_name, self.name = self.name.split(".", 1)

    @property
    def is_resend(self):
        return "." in self.true_name


class Message(MessageBase):
    def compile(self, context):
        context.add_literal_str_push_bytecode(self.name)

        send_type = SEND_TYPE_UNARY
        if self.is_resend:
            send_type = SEND_TYPE_UNARY_RESEND
            context.add_literal_str_push_bytecode(self.parent_name)

        context.add_bytecode(BYTECODE_SEND)
        context.add_bytecode(send_type)
        context.add_bytecode(0)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.name == obj.name

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "Message(%s)" % self.name


class KeywordMessage(MessageBase):
    def __init__(self, name, parameters):
        MessageBase.__init__(self, name)  # weird stuff
        self.parameters = parameters

    def compile(self, context):
        context.add_literal_str_push_bytecode(self.name)

        send_type = SEND_TYPE_KEYWORD
        if self.is_resend:
            send_type = SEND_TYPE_KEYWORD_RESEND
            context.add_literal_str_push_bytecode(self.parent_name)

        for parameter in reversed(self.parameters):
            parameter.compile(context)

        context.add_bytecode(BYTECODE_SEND)
        context.add_bytecode(send_type)
        context.add_bytecode(len(self.parameters))

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.name == obj.name and \
               self.parameters == obj.parameters

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        params = "[]"
        if self.parameters:
            assert isinstance(self.parameters[0], BaseBox)
            params = _repr_list_of_baseboxes(self.parameters)

        return "KeywordMessage(name=%s, parameters=%s)" % (self.name, params)


class BinaryMessage(BaseBox):
    def __init__(self, name, parameter):
        self.name = name
        self.parameter = parameter

    @property
    def is_resend(self):
        return False

    def compile(self, context):
        context.add_literal_str_push_bytecode(self.name)

        self.parameter.compile(context)

        context.add_bytecode(BYTECODE_SEND)
        context.add_bytecode(SEND_TYPE_BINARY)
        context.add_bytecode(1)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.name == obj.name and \
               self.parameter == obj.parameter

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "BinaryMessage(name=%s, parameter=%s)" % (
            self.name,
            self.parameter.__str__()
        )


class Send(BaseBox):
    def __init__(self, obj, msg):
        self.obj = obj
        self.msg = msg

    def compile(self, context):
        self.obj.compile(context)
        self.msg.compile(context)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.obj == obj.obj and \
               self.msg == obj.msg

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "Send(obj=%s, msg=%s)" % (
            self.obj.__str__(),
            self.msg.__str__()
        )


class Resend(BaseBox):
    def __init__(self, parent_name, msg):
        assert isinstance(parent_name, str)

        self.parent_name = parent_name
        self.msg = msg

    def compile(self, context):
        context.add_bytecode(BYTECODE_PUSH_SELF)
        self.msg.compile(context)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.parent_name == obj.parent_name and \
               self.msg == obj.msg

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "Resend(parent_name=%s, msg=%s)" % (
            self.parent_name,
            self.msg.__str__()
        )


def send_or_resend(obj, msg):
    if msg.is_resend:
        if obj != Self():
            raise ValueError("Can't send resend to %s" % obj.__str__())

        return Resend(msg.parent_name, msg)

    return Send(obj, msg)


class Cascade(BaseBox):
    def __init__(self, obj, msgs):
        self.obj = obj
        self.msgs = msgs

    def compile(self, context):
        for msg in self.msgs:
            self.obj.compile(context)
            msg.compile(context)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.obj == obj.obj and \
               self.msgs == obj.msgs

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        msgs = "[]"
        if self.msgs:
            msgs = _repr_list_of_baseboxes(self.msgs)

        return "Cascade(obj=%s, msgs=%s)" % (self.obj.__str__(), msgs)


class Return(BaseBox):
    def __init__(self, value):
        self.value = value

    def compile(self, context):
        self.value.compile(context)
        context.add_bytecode(BYTECODE_RETURN_IMPLICIT)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and \
               self.value == obj.value

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "Return(%s)" % self.value.__str__()


class AssignmentPrimitive(BaseBox):
    def compile(self, context):
        context.add_bytecode(BYTECODE_PUSH_LITERAL)
        context.add_bytecode(LITERAL_TYPE_ASSIGNMENT)
        context.add_bytecode(0)

        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__)

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return "AssignmentPrimitive()"


class Comment(BaseBox):
    def __init__(self, msg):
        self.msg = msg

    def compile(self, context):
        return context

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and self.msg == obj.msg

    def __ne__(self, obj):
        return not self.__eq__(obj)

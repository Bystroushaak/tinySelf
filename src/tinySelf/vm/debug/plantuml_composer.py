#! /usr/bin/env python3


def indent(content):
    return "\n".join(
        "    " + line if line else line
        for line in content.splitlines()
    )


class Root(object):
    def __init__(self, items=None):
        self.items = items if items else []

    def add(self, item):
        self.items.append(item)

    def pick_all_connections(self):
        pass

    def to_str(self):
        items = "\n".join(
            item.to_str() for item in self.items
        )

        connections = []
        for item in self.items:
            connections.extend(item.get_connections())

        content = items + "\n".join(connections)
        return "@startuml\n%s\n@enduml" % content


class Base(object):
    def raw_connect(self, raw_connect):
        self.connections.append(raw_connect)

    def connect(self, item, pos=None, type="-->", desc=""):
        item_name = item.name

        if pos:
            assert pos in "dulr"
            type = type[:1] + pos + type[1:]

        if not desc:
            self.raw_connect("%s %s %s" % (self.name, type, item_name))
        else:
            self.raw_connect("%s %s %s: %s" % (self.name, type, item_name, desc))


class Class(Base):
    def __init__(self, name, alt_name=None, prop=None, methods=None):
        self.name = name
        self.alt_name = alt_name

        self._class_type = "class"

        self.properties = prop if prop else []
        self.methods = methods if methods else []
        self.connections = []

    def add_property(self, raw_property):
        self.properties.append(raw_property.strip())

    def add_method(self, raw_method):
        self.methods.append(raw_method)

    def get_connections(self):
        return self.connections

    def _get_alt_name(self):
        return '%s %s as "%s" {\n' % (self._class_type, self.name, self.alt_name)

    def to_str(self):
        if self.alt_name:
            o = self._get_alt_name()  # because object has this backwards
        else:
            o = '%s %s {\n' % (self._class_type, self.name)

        if self.properties or self.methods:
            for item in self.properties:
                o += indent(item)
                o += "\n"

            if self.methods:
                o += indent("--") + "\n"

                for item in self.methods:
                    o += indent(item)
                    o += "\n"

        o += '}\n\n'

        return o


class Abstract(Class):
    def __init__(self, name, alt_name=None, prop=None, methods=None):
        super(Abstract, self).__init__(name, alt_name=alt_name, prop=prop, methods=methods)
        self._class_type = "abstract"


class Interface(Class):
    def __init__(self, name, alt_name=None, prop=None, methods=None):
        super(Interface, self).__init__(name, alt_name=alt_name, prop=prop, methods=methods)
        self._class_type = "interface"


class Annotation(Class):
    def __init__(self, name, alt_name=None, prop=None, methods=None):
        super(Annotation, self).__init__(name, alt_name=alt_name, prop=prop, methods=methods)
        self._class_type = "annotation"


class Enum(Class):
    def __init__(self, name, alt_name=None, prop=None, methods=None):
        super(Enum, self).__init__(name, alt_name=alt_name, prop=prop, methods=methods)
        self._class_type = "enum"


class Object(Class):
    def __init__(self, name, alt_name=None, prop=None, methods=None):
        super(Object, self).__init__(name, alt_name=alt_name, prop=prop, methods=methods)
        self._class_type = "object"

    def _get_alt_name(self):
        return '%s "%s" as %s {\n' % (self._class_type, self.alt_name, self.name)


class Package(Base):
    def __init__(self, name, items=None):
        self.name = name
        self._package_type = "package"

        self.items = items if items else []
        self.connections = []

    def add(self, item):
        self.items.append(item)

    def get_connections(self):
        connections = self.connections[:]
        for item in self.items:
            connections.extend(item.get_connections())

        return connections

    def to_str(self):
        o = '%s %s {\n' % (self._package_type, self.name)

        for item in self.items:
            o += indent(item.to_str())

        o += "}\n\n"

        return o


class Node(Package):
    def __init__(self, name, items=None):
        super(Node, self).__init__(name, items)
        self._package_type = "node"


class Folder(Package):
    def __init__(self, name, items=None):
        super(Folder, self).__init__(name, items)
        self._package_type = "folder"


class Frame(Package):
    def __init__(self, name, items=None):
        super(Frame, self).__init__(name, items)
        self._package_type = "frame"


class Cloud(Package):
    def __init__(self, name, items=None):
        super(Cloud, self).__init__(name, items)
        self._package_type = "cloud"


class Database(Package):
    def __init__(self, name, items=None):
        super(Database, self).__init__(name, items)
        self._package_type = "database"


if __name__ == '__main__':
    c = Class("xe", prop=["prop"], methods=["+ .method()"])
    d = Object("xex")
    c.connect(d)

    p = Frame("test", [c, d])

    root = Root([p])
    print(root.to_str())

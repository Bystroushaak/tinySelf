# -*- coding: utf-8 -*-
import inspect


def create_copy_with_different_types(cls, new_name, other_replacements=None):
    """
    Create copy of the `cls` item with `new_name`. Also optionally run
    .replace() calls on the source for all pairs in `other_replacements`.

    This function is useful as kind of template for generalization of code.

    For example, when you create a new container object, type annotator assigns
    types to each property when it is first used. You can't use it for other
    types as well. Other languages (Java, C++) solve this problem by using
    templating, but RPython provides no such way, so I am using code generation
    on the source level to generate another class with exact same source code,
    but different names.

    Args:
        cls (class): Some class you wish to copy.
        new_name (str): New name for the class.
        other_replacements (list of pairs, default None): Other string
            replacements. Literally just bunch of .replace() calls for each
            pair.

    Returns:
        str: Modified source. Use exec .. to generate code on the fly.
    """
    source = "".join(inspect.getsourcelines(cls)[0])
    source = source.replace(cls.__name__, new_name)

    if other_replacements is not None:
        for item in other_replacements:
            source = source.replace(*item)

    return source

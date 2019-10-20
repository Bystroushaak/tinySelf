# -*- coding: utf-8 -*-

VERSION = "0.0.1"

# Use MethodStack based on LinkedList (=True) or PreallocatedArray (=False)?
# LinkedList is faster with JIT, and PreallocatedArray without it.
USE_LINKED_LIST_METHOD_STACK = True

STDLIB_PATHS = "objects/stdlib.tself:/var/lib/tinySelf/stdlib.tself"
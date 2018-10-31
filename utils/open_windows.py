#! /usr/bin/env python3
import os.path

import sh


if __name__ == '__main__':
    tinySelf_root_path = os.path.join(os.path.dirname(__file__), "../")
    tinySelf_root_path = os.path.abspath(tinySelf_root_path)

    sh.caja(tinySelf_root_path)
    sh.caja(os.path.join(tinySelf_root_path, "tests"))
    sh.caja(os.path.join(tinySelf_root_path, "src/tinySelf/parser"))
    sh.caja(os.path.join(tinySelf_root_path, "src/tinySelf/vm"))
    sh.mate_terminal(working_directory=tinySelf_root_path)

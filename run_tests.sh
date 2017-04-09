#! /usr/bin/env sh
export PYTHONPATH="src:$PYTHONPATH:/home/bystrousak/Plocha/tests/pypy/rpython"

python -m pytest tests $@
# python3 -m pytest tests $@
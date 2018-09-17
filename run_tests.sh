#! /usr/bin/env bash
export PYTHONPATH="src/:$PYTHONPATH"

if [ -e "tests/__pycache__" ]; then
    rm -fr "tests/__pycache__"
fi

if [ -e "tests/vm/__pycache__" ]; then
    rm -fr "tests/vm/__pycache__"
fi

python2 -m py.test tests $@

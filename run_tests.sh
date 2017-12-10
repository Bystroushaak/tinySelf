#! /usr/bin/env bash
export PYTHONPATH="src/:$PYTHONPATH"

python2 -m py.test tests $@
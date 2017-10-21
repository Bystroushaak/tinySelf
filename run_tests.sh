#! /usr/bin/env bash
export PYTHONPATH="src/:$PYTHONPATH"

py.test tests $@
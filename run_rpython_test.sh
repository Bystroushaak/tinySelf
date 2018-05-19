#! /usr/bin/env bash

function print_help() {
    echo "Help:"
    echo -e "\t-q Jump out of the pypy's pdb shell in case of error."
    echo -e "\t-h Print this help."
    exit
}


exit_from_pdb=false
while getopts "hq" opt; do
    case $opt in
    q) exit_from_pdb=true ;;
    h) print_help ;;
    \?) print_help ;;
    esac
done


# export $PATH="/home/bystrousak/Plocha/tests/pypy/:$PATH"
if $exit_from_pdb; then
    echo "exit" | $HOME/Plocha/tests/pypy/rpython/bin/rpython --output tSelf src/tinySelf/target.py
else
    $HOME/Plocha/tests/pypy/rpython/bin/rpython --output tSelf src/tinySelf/target.py
fi

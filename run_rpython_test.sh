#! /usr/bin/env bash

OUTPUT_FN="tSelf"
TARGET_FN="src/tinySelf/target.py"


function print_help() {
    echo
    echo "Help:"
    echo -e "\t-q Jump out of the pypy's pdb shell in case of error."
    echo
    echo -e "\t-d Don't optimize. Useful for debugging purposes."
    echo
    echo -e "\t-h Print this help."
    echo
    exit
}


dont_optimize=false
exit_from_pdb=false
while getopts "hqd" opt; do
    case $opt in
    q) exit_from_pdb=true ;;
    h) print_help ;;
    d) dont_optimize=true ;;
    \?) print_help ;;
    esac
done


RPYTHON_PARAMS="--output $OUTPUT_FN $TARGET_FN"
if $dont_optimize; then
    RPYTHON_PARAMS="--opt=1 --gc=minimark $RPYTHON_PARAMS"
fi


# export $PATH="/home/bystrousak/Plocha/tests/pypy/:$PATH"
if $exit_from_pdb; then
    echo "exit" | $HOME/Plocha/tests/pypy/rpython/bin/rpython $RPYTHON_PARAMS
else
    $HOME/Plocha/tests/pypy/rpython/bin/rpython $RPYTHON_PARAMS
fi

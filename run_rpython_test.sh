#! /usr/bin/env bash

# export $PATH="/home/bystrousak/Plocha/tests/pypy/:$PATH"
# $HOME/Plocha/tests/pypy/rpython/bin/rpython src/tinySelf/target.py

expect <<EOL
set timeout 10000
spawn $HOME/Plocha/tests/pypy/rpython/bin/rpython --gc=minimark --opt=0 src/tinySelf/target.py

expect {
    "(Pdb+) "
}

close
EOL

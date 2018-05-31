#!/bin/bash
#read_excel.bash

function FINDCLASS() {
    cat $1 | grep '^[A-Z][A-Z][A-Z][A-Z][0-9][0-9][0-9]M'  # ([A-Z]){3,4}([0-9]){3,4}M
}

# [0] Code
# [1] Title
# [0]
# [0]

FINDCLASS Test.txt


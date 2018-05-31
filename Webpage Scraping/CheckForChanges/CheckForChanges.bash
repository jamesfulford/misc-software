function lsdiff() {
    # Does a recursive ls of first argument (directory)
    # and stores it in second argument (or in $1/../.dirlisting)
    #   take care that $2 isn't below $1

    if [[ $# > 1 ]]; then
        readfile="$2"
    else
        readfile="$1/../.dirlisting"
    fi

    if [ -f "$readfile" ]; then
        diff -u <(ls -Ril "$1") <(cat "$readfile") |
        grep "^[+-]" |
        grep -v "+++" |
        grep -v "\-\-\-"
    fi

    ls -Ril "$1" > "$readfile"
}


lsdiff "/Users/jamesfulford/Desktop" "/Users/jamesfulford/DesktopListingStorage"
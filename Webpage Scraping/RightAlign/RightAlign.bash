#!/bin/bash
# RightAlign.bash
# by James Fulford
# checks pages to see if things are right-aligned.

function checkpage {
    curl -L -s $1 > page
    grep -i -c '<h5>Total Credits - ' page > credits
    grep -i -c '<td colspan=\"5\" class=\"text-right\"' page > rights
    diff -a credits rights

    if [ $? == 1 ]; then
        echo "$(date),Right Align Check failed,"$1 >> Checks.csv
    else
        echo "Fine "$1
    fi
    rm credits rights page
}

link='http://www.mccnh.edu/academics/programs/'
curl -s $link | grep 'href="/academics/programs/' | sed 's@.*href="/academics/programs/@@' | sed 's/".*//' | sed 's/#.*//'> links.txt
cat links.txt | sort -u > out.txt

for file in $(cat out.txt); do
    checkpage $link$file
done

rm links.txt out.txt
#!/bin/bash
# ReadCertsFromPages.bash
# by James Fulford
# checks pages to see if things are right-aligned.

function checkpage {
    curl -L -s $1 > page

}

link='http://www.mccnh.edu/academics/programs/'

curl -s $link |
grep 'href="/academics/programs/' |
sed 's@.*href="/academics/programs/@@' |
sed 's/".*//' |
grep "#" > links.txt

cat links.txt | sed 's/.*#//' > ids.txt
cat links.txt | sed 's/#.*//' > lin.txt

#
# need to iterate over lin.txt and ids.txt at the same time!
# lin.txt by $file
# ids.txt by $id
#
# for file in $(cat lin.txt | sed 's/#.*//'); do
for l in $(cat links.txt); do
    file=$(echo $l | sed 's/#.*//')
    id=$(echo $l | sed 's/.*#//')

    end="</html>"


    a=$(curl -L -s $link$file)
    a="$(echo "${a#*"$id"}")"

    a=$(echo "$id${a%%"$end"*}$end" |  # will remove all before cert section
    sed "s/$id.*//")  # removes broken html at top

    end="</table>"
    a="$(echo "${a#*"<table"}")"
    echo "<table${a%%"$end"*}$end" |  # will remove before the first table in cert section
    grep -A 4 "[A-Z]\{3\}[0-9]\{3\}M" |  # gets lines with course codes on them plus 4 tds after them.
    sed "s/<\/td>//g" | sed "s/<td>//g" |  # removes <td> and </td>
    sed "s@.*/item/@@g" |  # removes link, leaves k2id
    sed $'s/\" class=\"jcepopup\">/\\\n/' |  # removes rest of link
    sed "s@</a>@@"  # removes closing a tag
    # tr "\r\n" , #|  # replaces new lines with commas
    # sed "s/,,/,/" > "$file$id.txt"  # removes repeating commas (incase of \r\n)

    # Expected output will follow this format for each comma-separated line:
    # [0] Course code
    # [1] K2 id
    # [2] Course title
    # [3] Theory or Lecture credits
    # [4] Lab credits
    # [5] Total credits
done

# rm links.txt out.txt
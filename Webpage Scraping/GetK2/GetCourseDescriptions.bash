#!/bin/bash

echo 1,$(curl -L -s 'http://www.mccnh.edu/component/k2/item/1' |
grep -A 1 "<h1>" |
sed '/<h1>/d' |
awk '{$1=$1};1' |
sed 's/ - /,/g' |
sed 's/ (/,/' |
sed 's/)//' |
sed 's/-/,/g') > k2items.csv

for i in `seq 2 2300`; do
    echo $i,$(curl -L -s 'http://www.mccnh.edu/component/k2/item/'$i |
    grep -A 1 "<h1>" |
    sed '/<h1>/d' |
    awk '{$1=$1};1' |
    sed 's/ - /,/g' |
    sed 's/ (/,/' |
    sed 's/)//' |
    sed 's/-/,/g') >> k2items.csv
done

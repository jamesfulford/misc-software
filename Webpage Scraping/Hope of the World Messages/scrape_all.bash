echo "message_id,title,date" > finished.csv
page=0

while true
do

    curl -s "http://www.hopeoftheworld.org/Order/index.php?pageNum_WADAmessageinfo=${page}&totalRows_WADAmessageinfo=2095" > 1curl2

    if [[ $(cat 1curl2) != *"<html"* ]]; then
        break
    fi

    #
    # Ids
    #
    cat 1curl2 |
    grep "Msg #: " |
    sed "s/<th scope=\"col\" align=\"left\" width=\"150px\">Msg #: //" |
    sed "s/<\/th>//" |
    perl -pe 's/^\s+//' > ids.txt

    #
    # Dates
    #
    cat 1curl2 |
    grep "Date: " |
    sed "s/<th scope=\"col\" align=\"left\" width=\"450px\">Date: //" |
    sed "s/<!--POPUP-->//" |
    perl -pe 's/\s+//' |
    perl -pe 's/ +//g' > date.txt

    #
    # Titles
    #
    cat 1curl2 |
    grep "<th colspan=\"2\" scope=\"col\" align=\"left\">" |
    sed "s/<th colspan=\"2\" scope=\"col\" align=\"left\">//" |
    sed "s/<\/th>//" |
    perl -pe 's/^\s+//' > title.txt


    len=$(cat ids.txt | wc -l | perl -pe 's/^\s+//')
    for (( i=1; i<=$len; i=i+1 ))
    do
    	title=$(cat title.txt | head -$i | tail -1 | tr -d '\r\n')
    	dates=$(cat date.txt | head -$i | tail -1 | tr -d '\r\n')
    	ids=$(cat ids.txt | head -$i | tail -1 | tr -d '\r\n')
    	echo "$ids,$title,$dates" >> finished.csv
    done

    #
    # Next page
    #
    echo $page has $len entries.
    ((page++))

done

rm 1curl2 title.txt date.txt ids.txt

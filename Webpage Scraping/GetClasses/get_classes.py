# get_classes.py
# by James Fulford

from bs4 import BeautifulSoup as Soup
from urllib2 import urlopen
import csv

link = "http://www.mccnh.edu/academics/course-schedules/fall-2017"

sup = Soup(urlopen(link).read(), "html.parser")
trs = sup.find_all("table")[0].find_all("tr")
trs = map(lambda t: map(lambda d: d.get_text().strip(), t.find_all("td")), trs)
trs = filter(lambda l: len(l) > 0, trs)
trs.sort(key=lambda x: x[1])

with open("output.csv", "w") as phile:
    wr = csv.writer(phile)
    wr.writerow(["CRN", "CODE", "TITLE", "CR", "DATE", "DAYS", "TIME", "COST"])
    for tr in trs:
        wr.writerow(tr)

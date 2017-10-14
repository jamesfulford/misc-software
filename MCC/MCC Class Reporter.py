 # MCC Class Reporter.py
# python 2.7 (or so)
# by James Fulford


# Reads from links.txt (or path in first command line argument)
# and scrapes pages and generates reports
# Takes CCSNH class details page and parses.
#       beauty may have been lost somewhere. But, effectiveness has been picked up.

# Started 7/9/2016
# Ended 7/17/2016
# Added Command Line Argument option 12/24/2016

# Jing #1: http://screencast.com/t/ZoGINvSwG
# Jing #2: http://screencast.com/t/WkoIinNB8


import requests
from bs4 import BeautifulSoup
import json
import copy
import os
import sys

"""
Global Variables:
"""
classes = {}  # will be populated with data on classes


"""
Functions:
"""

def make_links(prequel, file_name):
    """
    returns a list of links with crns of each line
    in file_name
    If could not find links.txt,
    then asks for a single crn.
    """
    if(os.path.exists(file_name)):
        try:
            print("}}}} Found " + file_name + " file. Crafting links...\n\n")
            phile = open(file_name, "r")
            crns = phile.readlines()
            phile.close()
            cleaned_crns = prefix_clean(prequel, crns)
            print("}}}} Done crafting links.\n\n")
            return(cleaned_crns)
        except IOError, Argument:
            print("Error in accessing " + file_name + "\n>>> " + str(Argument) + "\n\n")
    else:
        print("Could not find " + file_name + " in present directory: " + str(os.getcwd()))
        try:
            crns = []
            while True:
                crn = ask_crn()
                if("s" in crn):
                    raise Exception
                crns.append(str(crn))
        finally:
            print("}}}} Done crafting links.\n\n")
            return(prefix_clean(prequel, crns))


def verify_crn(crn):  # helper: make_links, ask_crn
    """
    Returns whether given crn is of a legitimate format.
    """
    if(len(crn.rstrip("\n")) == 5):
        return True
    return False


def prefix_clean(prestr, listing):  # helper: make_links
    temp_list = copy.deepcopy(listing)
    for entry in temp_list:
        if(not verify_crn(entry)):
            temp_list.remove(entry)
    for i in range(0, len(temp_list)):
        temp_list[i] = str(prestr) + str(temp_list[i]).rstrip("\n")
    return(list(set(temp_list)))


def ask_crn():  # helper: make_links
    try:
        result = str(raw_input("Provide a 5 digit crn (\"s\" to quit):"))
        print(result)
        if("s" not in result):
            assert(verify_crn(result))
        return result
    except:
        print("Error: please ensure input was 5 digit crn.\n")
        return ask_crn()


def make_soup(links):
    """
    accepts a list of links
    returns a list of BeautifulSoups, one for each link given by links.
    """
    bbb_soups = []  # Beautiful Beautiful Beautiful Soups!
    print("}}}} Retrieving and parsing data from links...\n\n")
    for every_link in links:
        try:
            request = requests.get(every_link)
            soup = BeautifulSoup(request.content, "html.parser")
            if(len(soup.find_all("th", {"class": "ddlabel"})) > 0):
                # has labels (unlike empty or error pages)
                if("\\" not in name(soup) and "/" not in name(soup)):
                    # has nice name (so report names don't cause path problems)
                    bbb_soups.append(soup)  # then, keep the soup
        except IOError, Argument:
            print("Could not retrieve " + every_link + "\n>>> " + str(Argument) + "\n\n")
    print("}}}} Finished getting and parsing data from links.\n\n")
    return bbb_soups


def name(soup):  # helper: make_soup, extract_data
    """
    Returns name of particular course.
    """
    label = extract_label(soup)
    return str(label[0]).split("-")[0][:-1]


def extract_data(soups):
    """
    Takes all the soups, cleans data, and makes reports.
    one (1) report in json for each course
    two (2) reports for all classes, one in json and one in csv
    """
    print("}}}} Extracting data...")
    descriptor = ["Seat Capacity", "Seats Taken", "Seats Remaining",
                  "Waitlist Seats", "Waitlist Seats Taken",
                  "Waitlist Seats Available"]
    for soup in soups:
        # finds and cleans all table data with dddefault class
        tables = soup.find_all("td", {"class": "dddefault"})
        for i in range(0, len(tables)):
            tables[i] = tables[i].text  # get rid of tags, attributes, etc.

        # building dictionary about this course
        data = {}
        data["Course Title"] = name(soup)
        for i in range(0, len(descriptor)):
            data[descriptor[i]] = tables[i + 1]

        # exporting to individual json reports
        prettydata = json.dumps(data, sort_keys=True, indent=4)
        dump(prettydata, name(soup))

        # storing data in "classes" dictionary (global)
        classes[name(soup)] = data

        # ending loop:   for soup in soups:
    print("   } Exported individual reports...")
    # exporting compilation json
    jString = json.dumps(classes, sort_keys=True, indent=4)
    dump(jString, "Compilation of Classes.txt")
    print("   } Exported JSON full report...")

    # exporting compilation csv
    csv = ""
    headings = ["Course Title"]
    for heading in copy.deepcopy(descriptor):  # copy to avoid pointer problems
        headings.append(heading)  # recycling earlier list, keep it simple

    csv += delimit(headings, ",")  # adding headers to csv

    for course in classes.keys():
        csv += "\n" + course  # adding course name
        csv += "," + delimit(list_dictionary(classes[course]), ",")  # adding information
    dump(csv, "Compilation of Classes.csv")  # exporting all data in csv string
    print("   } Exported CSV full report...")
    print("}}}} Finished extracting data.\n\n")

def delimit(strings, delimiter):  # helper: extract_data
    """
    accepts a list and a delimiter,
    returns every entry in the list punctuated with a delimiter.
    for example: delimit(["apple", "pineapple", "pear"], ",")
    will return: "apple, pineapple, pear"
    """
    result = ""
    for entry in strings:
        result += str(entry)
        if(strings.index(entry) < len(strings) - 1):
            result += delimiter
    return result
    # end extract_data

def list_dictionary(diction):  # helper: extract_data
    """
    Converts one entry's data in classes dictionary
    into a list.
    """
    result = []
    for entry in diction.keys():
        result.append(diction[entry])
    return result


def dump(data, title):  # helper: extract_data
    """
    Dumps file out in present directory.
    """
    try:
        phile = open(title, "wb")
        # will create file if doesn't exist.
        phile.write(str(data))
        phile.close()
    except IOError, Argument:
        error_string = "Error in dumping data to " + title + "\n    "
        error_string += str(os.getcwd()) + "\n>>> "
        error_string += str(Argument) + "\n\n"
        print(error_string)


def extract_label(soup):  # helper: extract_data
    """
    Accepts one soup.
    Returns text of all soup's table headers, in a list.
    """
    labels = soup.find_all("th", {"class": "ddlabel"})
    # finds all table headers with ddlabel class
    for i in range(0, len(labels)):
        labels[i] = labels[i].text  # cleans data
    return labels


"""
Instantiations:
"""
link_base = "https://sis.ccsnh.edu/PROD/bwckschd.p_disp_detail_sched?term_in=201630&crn_in="

path = "links.txt"
if(len(sys.argv) == 2):
    if(os.path.exists(sys.argv[1])):
        path = sys.argv[1]
    else:
        print("Provided links file could not be found: " + sys.argv[1])
list_of_links = make_links(link_base, "links.txt")
beholders = make_soup(list_of_links)

if(not os.path.exists("Reports")):
    os.makedirs("Reports")
os.chdir("Reports")  # now, reports will come up in their own directory.

extract_data(beholders)
print("End of process. Check " + str(os.getcwd()) + "\nfor all reports.")

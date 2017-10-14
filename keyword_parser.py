# keyword_parser.py
# by James Fulford

# https://docs.python.org/2.7/library/htmlparser.html
# https://docs.python.org/3/howto/urllib2.html
# http://www.tutorialspoint.com/python/python_files_io.htm
# https://docs.python.org/2/library/os.html
# https://docs.python.org/2/howto/sorting.html


# When we finally figure out Unicode:
    # http://stackoverflow.com/questions/6797984/how-to-convert-string-to-lowercase-in-python?rq=1
    # http://stackoverflow.com/questions/10569438/how-to-print-unicode-character-in-python
    # http://stackoverflow.com/questions/728891/correct-way-to-define-python-source-code-encoding?lq=1
    # https://docs.python.org/2/howto/unicode.html

from HTMLParser import HTMLParser
import urllib

header_text = """
<html>
<header> <title>Parser Report</title></header>
<body> <h1>Report: Website Parsing</h1><br/>
<h2> Listing of all keywords on this page and pages it links to. </h2><br/>
<p> A keyword is the text that goes between "a" tags. </p><br/>
<h2> Parsing:
"""


def clean(string):
    return string.strip("./@#^()_+=\|[]\{\}<>?! ")


def accept(this_string):
    if("{" in this_string or "}" in this_string):  # sifts out most Javascript
        return False
    if("<" in this_string or ">" in this_string):  # probably won't happen
        return False
    if(len(this_string) < 5 or len(this_string) > 60):  # make sure the ones without useful data are out
        return False
    return True


class KeywordParser(HTMLParser):
    in_a_tag = False
    keywords = {}
    links = {}
    def parse_url(self, url):
        get_data = urllib.urlopen(url).read()
        print("Received Response from " + str(url))
        self.url = url
        self.link_crement(url)
        self.feed(unicode(get_data))

    def parse_deep_url(self, url, distance):
        pass
        # one day, implement so it parses url, go out {distance} links and parse all those pages.
        # Therefore, this is a spider that indexes nearby sites (almost a "local spider").

    def handle_starttag(self, tag, attrs):
        if(tag == "a"):
            for attr in attrs:
                if attr[0] == u"href":
                    self.link_crement(attr[1])
            self.in_a_tag = True

    def handle_endtag(self, tag):
        if(tag is "a"):
            self.in_a_tag = False

    def handle_data(self, data):
        if(self.in_a_tag):
            if(accept(data)):
                self.keyword_crement(clean(data.lower()))

    def keyword_crement(self, data):
        if(data in self.keywords.keys()):
            self.keywords[data] += 1
        else:
            self.keywords[data] = 1

    def link_crement(self, link):
        if(link in self.links.keys()):
            self.links[link] += 1
        else:
            self.links[link] = 1

    def write_to_file(self, path):
        phile = open(path, "wb")
        phile.write(header_text)
        phile.write(self.url + "</h2><br/>")
        phile.write("<ol>")
        for entry in self.list_keywords():
            phile.write("<li>" + (entry[0]) + ": " + unicode(entry[1]) + "</li><br/>")
        phile.write("</ol></body></html>")
        phile.close()

    def list_keywords(self):
        return_list = []
        for entry in self.keywords.keys():
            return_list.append((entry, self.keywords[entry]))
        return_list.sort(key=lambda x: x[1], reverse=True)
        return return_list

# Now, to instantiation and other actions.

parser = KeywordParser()
url = "http://www.tutorialspoint.com"
parser.parse_url(url)
# parser.write_to_file('/Users/jamesfulford/James Fulford Imported Data.html')


step1 = KeywordParser()
for link in parser.links.keys():
    try:
        step1.parse_url(link)
    except:
        try:
            step1.parse_url(url + link)  # just in case the link stays on this site.
        except:
            print("Could not reach url: ", link)  # give up at this point
        else:
            print("Success: ", url + link)
    else:
        print("Success: ", link)

step1.write_to_file('/Users/jamesfulford/James Fulford Report.html')

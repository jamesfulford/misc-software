from collections import OrderedDict
from copy import deepcopy
import datetime
import json

from bs4 import BeautifulSoup as Soup


#
# Constants
#
PARSE_LOGIN_TRIGGERS = {
    "Pre Software Update": "pre_login",
    "Pre-software Update": "pre_login",

    "Post Software Update": "post_login",
    "Post-software Update": "post_login",
}  # used by login table parser
REPORT_JSON = "reports.json"


#
# Utilities
#
def try_int(val):
    try:
        return int(val)
    except ValueError:
        return None


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            return repr(o)


def iden(report):
    """
    Returns hashable identifier of a report
    """
    return "{} - {}".format(
        report["conversationid"],
        report["environment"]
    )


def resolve_environment(target):
    t = target.replace("_CLONE", "").replace("CLONE", "").upper()
    t = t.replace("_CLONE", "").replace("CLONE", "")
    t = t.replace(" ", "_")
    return t


#
# Parsers
#
def parse_post_table(table):
    data = {}
    for row in table.find_all("tr"):
        key, val = tuple(row.find_all("td"))
        data[key.text] = val.text
    return {
        "target_version": data["Update Software Version"].upper(),
        "source_version": data["Current Software Version"].upper(),
        "environment": resolve_environment(
            data["SitePortal Environment Name"]
        )
    }


def parse_login_table(table):
    data = {}
    rows = table.find_all("tr")

    for i in range(len(rows)):
        row = rows[i]

        for table_trigger, end_val in PARSE_LOGIN_TRIGGERS.items():
            if table_trigger in row.text:
                tds = rows[i + 1].find_all("td")
                # print map(lambda t: t.text, tds)
                for i in range(len(tds)):
                    if "Login" in tds[i].text:
                        val = tds[i + 1].text
                        # print val
                        break
                # val = rows[i + 1].find_all("td")[3].text
                val = val.replace("s", "")
                val = try_int(val)
                data[end_val] = val
    return data


def parse_alarm_row(row):
    cells = row.find_all("td")
    cells = map(lambda c: c.text, cells)
    while len(cells) < 9:
        cells.append(None)
    return {
        "vendor": cells[0],
        "model": cells[1],
        "description": cells[2],
        "severity": cells[3],
        "qty_device": try_int(cells[4]),
        "count_raised": try_int(cells[5]),
        "new_or_changed": True if cells[6] != "NO" else False,
        "method": cells[7],
        "notes": cells[8],
    }


def parse_alarm_table(table):
    return {
        "alarms": map(parse_alarm_row, table.find_all("tr")[1:])
    }


#
# Decide which parser to use based on contents of first cell in table
#
FIRST_CELL_TO_PARSER = OrderedDict([
    ("Date", parse_post_table),

    ("Vender", parse_alarm_table),
    ("Vendor", parse_alarm_table),

    ("Latency Testing (sec)", parse_login_table),
    ("Latency Testing (seconds)", parse_login_table),
])


def get_report_info(email):
    """
    Extracts list of report dictionaries from reports in given email
        and includes email metadata in each
    """
    print email.SentOn, email.Subject
    email_data = {
        "engineer": email.SenderName,
        "sent": datetime.datetime.fromtimestamp(int(email.SentOn)),
        "mirror": "mirror" in email.Subject.lower(),
        "live": "live" in email.Subject.lower(),
        "subject": email.Subject,
        "conversationid": email.ConversationID
    }
    tables = Soup(email.HTMLBody, "lxml").find_all("table")

    postings = []
    parse = False
    parsed = {}
    for i in range(len(tables)):
        table = tables[i]
        first_cell = table.find_all("td")[0].text

        if first_cell == FIRST_CELL_TO_PARSER.keys()[0]:
            if parse:
                postings.append(parsed)  # end of a report
            else:
                parse = True  # first report
            parsed = deepcopy(email_data)

        if parse and first_cell in FIRST_CELL_TO_PARSER:
            parsed.update(FIRST_CELL_TO_PARSER[first_cell](table))
        elif parse:
            pass
        # print i, first_cell, parse, len(postings)
    if parsed:
        postings.append(parsed)

    return postings

import argparse
from copy import deepcopy
import os

import pandas as pd

from css import config
from css.outlook import MAPI
from css.parsing import read_cache
from css.parsing import reports as reporting
from css.parsing import utilities as u


def print_env_states():

    parser = argparse.ArgumentParser()
    parser.add_argument("--ordering", default="highest")
    parser.add_argument("--target-version")
    args = parser.parse_args()

    UNMIRRORED = read_cache.get_last_report_dict()
    if args.target_version:
        UNMIRRORED = filter(
            lambda x: args.target_version not in x["target_version"],
            UNMIRRORED
        )

    def ordering(x):
        return {
            "highest": (x["target_version"], x["environment"]),
            "current": (
                read_cache.get_current_version(x),
                x["target_version"],
                x["environment"]
            ),
            "alphabetical": x["environment"],
        }[args.ordering]

    for rep in sorted(UNMIRRORED, key=ordering):

        print rep["environment"].rjust(
            max(map(len, map(lambda r: r["environment"], UNMIRRORED)))
        ), read_cache.get_current_version(rep).ljust(13), \
            "=> " + rep["target_version"] if not rep["live"] else ""

    print
    print "These are based on the most recent reports for each environment."
    print "If a report had incorrect information, this would not detect it!"


def parse_reports():
    # Extract report info from report emails
    REPORT_EMAILS = MAPI.GetDefaultFolder(6).Folders[
        config.OUTLOOK_REPORTS_FOLDER
    ].Items
    REPORT_EMAILS = filter(
        lambda e: "TicketId:" not in e.Subject,
        REPORT_EMAILS
    )
    reports = reduce(
        lambda a, b: a + b,
        map(reporting.get_report_info, REPORT_EMAILS)  # TODO: parallelize this
    )

    # add in more fields, do transformations
    for report in reports:
        report["id"] = reporting.iden(report)
        if "alarms" in report:
            report["count_alarm_types"] = len(report["alarms"])
            report["rebuild_rows"] = len(filter(
                lambda a: (
                    "rebuild" in a["description"].lower() and
                    ("toggl" not in a["notes"].lower() if a["notes"] else True)
                ),
                report["alarms"]
            ))
            report["non_toggle_rows"] = len(filter(
                lambda a: (
                    ("toggl" not in a["notes"].lower() if a["notes"] else True)
                ),
                report["alarms"]
            ))
        else:
            report["count_alarm_types"] = None
            report["rebuild_rows"] = None
            report["non_toggle_rows"] = None

    reports.sort(key=lambda x: x["sent"])

    # keep the earliest version of a report
    report_register = {}
    for report in reports:
        i = report["id"]
        if i in report_register.keys():
            if report_register[i]["sent"] > report["sent"]:
                report_register[i] = report
            else:
                pass
        else:
            report_register[i] = report
            # print "Added", report["id"], report["sent"]
    reports = report_register.values()

    # Dump into json cache
    print "Caching {} reports".format(len(reports))
    u.cache_records(
        os.path.join("reports", "reports.json"),
        reports
    )

    # Write spreadsheets
    excel_records = deepcopy(reports)
    for report in excel_records:
        report["date_completed"] = report["sent"].strftime("%Y-%m-%d")
        report["time_sent"] = report["sent"].strftime("%H:%M:%S")

    reports = pd.DataFrame(sorted(excel_records, key=lambda x: x["sent"]))
    reports.to_excel(
        os.path.join(config.DATA_DIR, "reports", "Reports.xlsx"),
        columns=[
            "date_completed",
            "environment",
            "live",
            "target_version",
            "source_version",
            "count_alarm_types",
            "rebuild_rows",
            "non_toggle_rows",
            "post_login",
            "pre_login",
            "time_sent",
            "engineer",
            "subject",
        ],
        index=False
    )

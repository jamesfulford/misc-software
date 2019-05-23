import os

from css.parsing import utilities as u


BLOCKLIST = [
]


def get_current_version(report):
    return report[
        "target_version" if report["live"] else "source_version"
    ].replace(" ", "")


def hash_env_name(env):
    return env.strip().replace("-", "").replace("_", "").upper()


def get_last_report_dict():
    cache = u.retrieve_cache(os.path.join("reports", "reports.json"))
    print "\tData gathered {}\n\n".format(cache["cache_time"])
    reports = cache["records"]

    LAST_REPORTS = {}
    for r in reports:
        e = hash_env_name(r["environment"])
        r["environment"] = e
        if e in LAST_REPORTS:
            if LAST_REPORTS[e]["sent"] < r["sent"]:
                LAST_REPORTS[e] = r
        else:
            LAST_REPORTS[e] = r
    LAST_REPORTS = LAST_REPORTS.values()
    LAST_REPORTS = filter(
        lambda r: r["environment"] not in BLOCKLIST,
        LAST_REPORTS
    )
    return LAST_REPORTS

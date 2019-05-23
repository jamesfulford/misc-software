# parse_log.py
# written by James Fulford, Software Release Engineer, March-April 2018

"""
TODO:
    - Group errors by association in output (nice to have)
    - Add more options to control output attributes (nice to have)

    - Adjust invocation association to permit association across parsers
        - thinking related errors may occur in different logs
        - do not lose specificity when comparing to parsers yielding
            less invocation information.
        = don't hash to get invocation right off the bat.
        = when comparing, find union of invocation-related keys
            and treat those as hashes
"""

import os
import re
from collections import OrderedDict
from datetime import datetime as dt
import gzip
import json
from copy import deepcopy
import logging


#
##
# Configuration
##
#

#
# Regular Expressions and Format Strings for parsers
#
BRACKETS = re.compile(r"\[(.*?)\]")  # selects text inside of hard brackets
GENERIC_ENVIRONMENT = re.compile(
    r"(?P<path>(?:/var/www/(?:cswapi_)?|/srv/generic-device-framework/)(?P<env>.*?)/.*?)[: #]"
)


#
# Filtering Configurations
#
# At least one of these keys must be present in a given line
# corresponding value is the severity such an error will be assigned.
# if conflicting severity, earlier beats later values (i.e. fatal beats minor)
ors = OrderedDict([
    ("fatal", "fatal"),
    ("error", "minor"),
    # ("exception", "minor")
])
#
# exclude
#
nots = [
    r" snmptrapd\[",
    r" CRON\[",
    r"not found or unable to stat",
    r"found, and server-generated directory index forbidden by Options directive",
    r"AH01797: client denied by server configuration",
]
nots = map(re.compile, nots)


#
##
# Internal Constants
##
#
JSONARGS = {
    "indent": 4,
    "sort_keys": True,
    "default": list  # handles sets
}
INVOCATION_KEY = "invocation"
ERROR_TYPE_KEY = "error_type"
SYSLOG_UNCATEGORIZED_ERROR_TYPE = "UNCATEGORIZED"
OUTFMT = "%Y-%m-%d %H:%M:%S"  # Output date format


#
# Utilities
#
def set_hash(attr, identifier):
    """
    Parser decorator which assigns value to "attr" attribute of output
        corresponding to the values of the attributes provided.

    (not in standard_transformations since it changes from parser to parser)
    """
    def hasher(f):
        def scraper(line):
            error = f(line)
            error[attr] = identifier(error)
            return error
        return scraper
    return hasher


def standard_transformations(fn):
    """
    Decorator which sets and transforms some fields returned by parsers.

    Requires following fields:
        "raw"
        "timestamp"

    """
    def transformer(*args):
        error = fn(*args)
        error.update({
            "timestamp": error["timestamp"],
            "raw": error["raw"],
            "severity": [
                v for i, v in ors.items() if i.lower() in error["raw"].lower()
            ][0],
            "environment": GENERIC_ENVIRONMENT.findall(error["raw"])[0][1],
            "file": GENERIC_ENVIRONMENT.findall(
                error["raw"]
            )[0][0] if "file" not in error else error["file"]
        })
        if "line" in error:
            error["line"] = int(error["line"])
        return error

    return transformer


def group_by(attr, items):
    """
    Returns dict keyed by attr's value in each item.
    """
    register = {}
    for i in items:
        register.setdefault(i[attr], [])
        register[i[attr]].append(i)
        del i[attr]
    return register


def reindex(d, fn=str):
    """
    Returns new dict with all keys passed through fn
    """
    r = {}
    for k, v in d.items():
        r[fn(k)] = v
    return r


def collate_group(group, no_collate_keys=None):
    """
    Returns dictionary keyed by groupnames and values are prototype dicts.

    A prototype is a dict with values being lists of prior values or a single
        representative value.
    """
    collated_items = {}
    if no_collate_keys is None:
        no_collate_keys = []
    no_collate_keys.append("_count")
    for group_name, items in group.items():
        prototype = {
            "_count": len(items)
        }

        # merge items into prototype
        for item in items:
            for key, value in item.items():
                prototype.setdefault(key, [])
                prototype[key].append(value)

        # if one value is representative of whole list,
        #   replace whole list with one representative value
        #   unless key is in no_collate_keys.
        for key, values in prototype.items():
            if key not in no_collate_keys:
                # simplify the value
                if all(isinstance(x, set) for x in values):
                    # take the union of all sets
                    prototype[key] = (
                        prototype[key] if isinstance(
                            prototype[key],
                            set
                        ) else set()
                    ).union(*values)
                elif len(set(values)) is 1:
                    # take a representative bit
                    prototype[key] = values[0]

        collated_items[group_name] = prototype

    return collated_items


def join_prototypes(a, p, ignore_keys=None):
    """
    Merges together two prototype dictionaries into one prototype dictionaries.

    Assumes listed prototype values are all equal length. If not,
        appended values will not line up.
    """
    ignore_keys = (
        (ignore_keys if ignore_keys is not None else []) + ["_count"]
    )
    new = deepcopy(a)
    for key, value in p.items():
        if key not in new:
            # if not going to overwrite, then go ahead
            new[key] = value
        else:
            # mitigate overwriting previous values

            # SPECIAL CASES
            if key == "associated":
                new[key] = new[key].union(value)
                continue
            elif key in ignore_keys:
                del new[key]
                continue

            # if old or new is listed, or are both vanilla but differ
            if (
                isinstance(a[key], list) or isinstance(p[key], list)
            ) or a[key] != p[key]:
                # make final result listed
                if not isinstance(a[key], list):
                    # expand original
                    new[key] = [new[key] for i in range(a["_count"])]

                if not isinstance(p[key], list):
                    # expand additional
                    new[key].extend([p[key] for i in range(p["_count"])])
                else:
                    # is already a list, add it on
                    new[key].extend(p[key])

            else:
                # both are equal vanilla values, and are still representative
                pass
    new["_count"] = a["_count"] + p["_count"]
    return new


#
##
# apache2/error.log parsing
##
#

# apache2/error.log
APACHE_INFMT = "%a %b %d %H:%M:%S.%f %Y"  # strptime date format string
APACHE_MESSAGE = re.compile(r"(.*?) in /var/www/.*? ")
APACHE_FILENAME = re.compile(r"in (/var/www/.*?) ")
APACHE_LINENO = re.compile(r"in /var/www/.*? on line ([1-9][0-9]*)")
APACHE_PID = re.compile(r"\[pid ([1-9][0-9]*)\]")


@set_hash(INVOCATION_KEY, lambda e: "{pid}: {timestamp}".format(**e))
@set_hash(ERROR_TYPE_KEY, lambda e: "{basename} - {message}".format(
    basename=os.path.basename(e["file"]),
    **e
))
@standard_transformations
def parse_apache_error(line):
    """
    All apache.log errors are the same format, so this is simple.
    """
    bracks = BRACKETS.findall(line)
    return {
        "raw": line,
        "timestamp": dt.strptime(bracks[0], APACHE_INFMT).strftime(OUTFMT),
        # "label": bracks[1].replace(":", ""),
        "pid": int(APACHE_PID.findall(line)[0]),
        "message": APACHE_MESSAGE.findall(
            "]".join(line.split("]")[4:])
        )[0].strip(),
        "file": APACHE_FILENAME.findall(line)[0],
        "line": APACHE_LINENO.findall(line)[0]
    }


#
##
# syslog parsing
##
#

#
# Constants
#
# In case two identical errors are sent to syslog at the same time,
# only one line is printed in the following format
SYSLOG_MULTI_INCIDENCE = re.compile(
    r"php: message repeated ([0-9])+ times: \[(.*)\]$"
)  # 0: repeats, 1: error message

SYSLOG_TS = re.compile(
    r"^([A-Za-z]{3}( +)[0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2})"
)
SYSLOG_INFMT = "%b %d %H:%M:%S"  # strptime format for Syslog output

# Array([attr] => value) format:
# found inside of results of SYSLOG_ARRAY, looking like (ignoring { and }):
#       [{key}] => {value}#012
# (the #012 stands for \n characters in syslog)
SYSLOG_ARRAY = re.compile(r"Array#012\(#012(.*?#012)\)")
SYSLOG_ATTR = re.compile(r"\[(.*?)\] => (.*?)#012")

SYSLOG_GDF = re.compile(
    r"Uncaught exception: Generic Device Trap Handler " +
    r"\(Vendor: (.*?), Model: (.*?)\) Critical Error#012Message: (.*?)" +
    r"#012#012Stack trace:#012#0 (.*?)\((.*?)\)"
)  # GDF Trap Handler regex


#
# Single incidence parsers
#
@set_hash(INVOCATION_KEY, lambda e: "{timestamp}".format(**e))
@set_hash(ERROR_TYPE_KEY, lambda e: "{basename} - {message}".format(
    basename=os.path.basename(e["file"]),
    **e
))
@standard_transformations
def syslog_array_parser(ret):
    # getting arbitrary attributes given in Array([key] => value) format
    array_contents = SYSLOG_ARRAY.findall(ret["raw"])[0]
    ret.update(dict(SYSLOG_ATTR.findall(array_contents)))
    ret.update({
        "type": int(ret["type"])
    })
    return ret


@set_hash(INVOCATION_KEY, lambda e: "{timestamp}".format(**e))
@set_hash(
    ERROR_TYPE_KEY,
    lambda e: "GDF Trap Handler: {vendor}, {model} - {message}".format(**e)
)
@standard_transformations
def syslog_gdf_trap_handler_parser(ret):
    u = SYSLOG_GDF.findall(ret["raw"])[0]
    ret.update({
        "vendor": u[0],
        "model": u[1],
        "message": u[2],
        "file": u[3],
        "line": u[4],
    })
    return ret


@set_hash(INVOCATION_KEY, lambda e: "{timestamp}".format(**e))
@set_hash(ERROR_TYPE_KEY, lambda e: "{basename} - {message}".format(
    basename=os.path.basename(e["file"]),
    **e
))
@standard_transformations
def syslog_fatal_parser(ret):
    parts = GENERIC_ENVIRONMENT.split(ret["raw"])
    pre, post = parts[0].strip(), parts[-1].strip()
    ret.update({
        "line": re.compile(r"AT LINE ([0-9]+) IN").findall(pre)[0],
        "message": post
    })
    return ret


@set_hash(INVOCATION_KEY, lambda e: "{timestamp}".format(**e))
@set_hash(ERROR_TYPE_KEY, lambda e: "{basename} - {message}".format(
    basename=os.path.basename(e["file"]),
    message=SYSLOG_UNCATEGORIZED_ERROR_TYPE,
    line="",
    **e
))
@standard_transformations
def syslog_default_parser(ret):
    return ret


SYSLOG_SINGLE_INCIDENCE_PARSERS = OrderedDict([
    (SYSLOG_ARRAY, syslog_array_parser),
    (SYSLOG_GDF, syslog_gdf_trap_handler_parser),
    (re.compile(r" FATAL "), syslog_fatal_parser),
    (re.compile(r".*"), syslog_default_parser),
])


#
# Upper level syslog parsers
#
def parse_syslog_error(line, ret=None):
    """
    Distributes parsing to several other parsers, each for a different type
        of syslog error.
    """
    # Bare minimum requirement of fields, if not already parsed
    if ret is None:
        value, repl = SYSLOG_TS.findall(line)[0]
        value = value.replace(repl, " ")  # normalize whitespace
        # Bare minimum requirement of fields
        ret = {
            "raw": line,
            "timestamp": dt.strptime(value, SYSLOG_INFMT).replace(
                year=dt.now().year
            ).strftime(OUTFMT)
        }

    if SYSLOG_MULTI_INCIDENCE.search(line) is not None:
        repeats, error = SYSLOG_MULTI_INCIDENCE.findall(line)[0]
        error = parse_syslog_error(error, ret=deepcopy(ret))
        return [deepcopy(error) for i in range(int(repeats))]

    for regex, parser in SYSLOG_SINGLE_INCIDENCE_PARSERS.items():
        if regex.search(line) is not None:
            return parser(ret)

    return ret

#
##
# Parsing
##
#


FILE_LINE_PARSERS = OrderedDict([
    ("syslog", parse_syslog_error),
    ("error.log", parse_apache_error),
])


#
# Higher level processes
#
def is_a_candidate(l):
    """
    If a line is worthy of mention, but not necessarily related to an
    environment, it is considered a candidate.
    """
    # print any(excep.search(l) is not None for excep in nots), l
    return any(
        o.lower() in l.lower() for o in ors.keys()
    ) and not any(
        excep.search(l) is not None for excep in nots
    )


def is_relevant_error(l, must_match=[]):
    return all(
        a.search(l) for a in must_match  # and
    ) if must_match else True


def is_environment_specific(l):
    return GENERIC_ENVIRONMENT.search(l) is not None


def parse_file(filename, must_match=[]):
    #
    # Open File
    #
    with gzip.open(filename) if ".gz" in filename else open(filename) as phile:
        candidates = filter(
            is_a_candidate,
            (l.strip() for l in phile)
        )

        # will attempt to parse
        errors = filter(
            lambda c: is_environment_specific(c) and is_relevant_error(
                c,
                must_match=must_match
            ),
            candidates
        )

        # will not attempt to parse
        unparsed = filter(
            lambda c: not is_environment_specific(c),
            candidates
        )

    #
    # Parse
    #
    parsed_errors = []
    parsed = False
    for basename_substring, parser in FILE_LINE_PARSERS.items():
        if basename_substring in os.path.basename(filename):
            for e in errors:
                try:
                    parsed_output = parser(e)
                    if isinstance(parsed_output, list):
                        # if multiple error incidents parsed out of one line
                        parsed_errors.extend(parsed_output)
                    else:
                        parsed_errors.append(parsed_output)
                except Exception as ex:
                    # Catch parsing errors
                    logging.error("ParsingError: {}\n\t{}\n\n".format(
                        ex, e
                    ))
                    if DEBUG:
                        logging.exception(ex)
            parsed = True
            break

    if not parsed:
        # append unparsed errors in unparsed
        logging.error("The log {} is not a parsing-supported log.".format(
            filename
        ))
        unparsed.extend(errors)
    else:
        for pe in parsed_errors:
            pe["error_file_source"] = filename

    return parsed_errors, unparsed


def associate_and_group_errors(errors):
        # Associate errors based on whether they are from the same invocation
        # or not

        invocations = group_by(INVOCATION_KEY, parsed_errors)
        for inv, associated_errors in invocations.items():
            # these are all associated with each other: add each one's
            # error_type to each other
            assocs = set(map(lambda x: x[ERROR_TYPE_KEY], associated_errors))
            # print assocs
            for error in associated_errors:
                error.setdefault("associated", set())
                error["associated"] = error["associated"].union(assocs)
                if error[ERROR_TYPE_KEY] in error["associated"]:
                    # do not contain self
                    error["associated"].remove(error[ERROR_TYPE_KEY])

        error_types = collate_group(
            group_by(ERROR_TYPE_KEY, parsed_errors),
            no_collate_keys=["timestamp", "raw", "pid", "line"]
        )

        return error_types


if __name__ == "__main__":

    import argparse

    args_parse = argparse.ArgumentParser(
        description=(
            "Parses logs for errors, groups errors, and provides basic"
            " information about each error."
        )
    )
    # Core functionality
    args_parse.add_argument(
        "-m",
        "--must_match",
        nargs="*",
        help="regex which included errors must match"
    )
    args_parse.add_argument(
        "-e",
        "--environments",
        nargs="*",
        help="environment(s) that should be filtered for, if any"
    )
    args_parse.add_argument("files", nargs="+", help="log files to parse")
    args_parse.add_argument(
        "-o",
        "--output",
        help="location to dump error type dictionary"
    )
    # Output preferences
    args_parse.add_argument(
        "-x",
        "--exclude-unparsed",
        default=False,
        action="store_true",
        help="does not print out unparsed errors"
    )
    args_parse.add_argument(
        "-q",
        default=0,
        action="count",
        help="display less information " +
             "(1: hide raw error, 2: hide association info," +
             " 3: hide metadata, 4+: silent)"
    )
    args_parse.add_argument(
        "--backlog",
        "-b",
        default=0,
        type=int,
        help="check older logs"
    )
    args_parse.add_argument(
        "--min-date",
        help="restrict errors to only those past given timestamp: Y-m-d H:M:S"
    )
    args_parse.add_argument(
        "--ignore-persisting",
        "-i",
        default=False,
        action="store_true",
        help="excludes error types occurred before and after min-date" +
        "(option ignored if --min-date not provided)"
    )

    args_parse.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        help="enable debugging mode"
    )

    # Parse and prepare arguments
    args = args_parse.parse_args()
    DEBUG = args.debug
    must_match = map(
        re.compile,
        args.must_match
    ) if args.must_match else []
    min_date = dt.strptime(args.min_date, OUTFMT) if args.min_date else None

    environments = map(
        str.lower, args.environments if args.environments else []
    )

    # all lines must include at least one of the environments given
    must_match.append(re.compile("(:?{})".format("|".join(environments))))

    if args.files:

        def log_exists(f):
            exist = os.path.exists(f)
            if not exist:
                logging.error("{} does not exist".format(f))
            return exist

        files = []
        for f in filter(log_exists, args.files):
            files.append(f)
            if args.backlog >= 1:
                one = f + ".1"
                if log_exists(one):
                    files.append(f + ".1")
                if args.backlog >= 2:
                    files.extend(filter(log_exists, [
                        "{}.{}.gz".format(f, i) for i in range(
                            2, args.backlog + 1
                        )
                    ]))

        if not files:
            raise OSError("No files specified exist")

    # Parse files and gather error types, unparsed errors
    # (Parsing failures are printed)
    #
    # TODO: parallel this because backlogs go insane
    #
    all_error_types = {}
    all_unparsed = []
    for log in files:

        parsed_errors, unparsed = parse_file(
            log,
            must_match=must_match
        )

        if environments:
            parsed_errors = filter(
                lambda x: x["environment"] in environments,
                parsed_errors
            )

        ets = associate_and_group_errors(parsed_errors)

        for error_type, prototype in ets.items():
            if error_type in all_error_types:
                all_error_types[error_type] = join_prototypes(
                    prototype,
                    all_error_types[error_type]
                )
                # later code for printing out raws assumes these
            else:
                all_error_types[error_type] = prototype
        all_unparsed.extend(unparsed)

    # Display output
    # print bool(all_unparsed), all_unparsed
    if not args.exclude_unparsed:
        print
        print "=" * 80
        print
        print "\n".join(all_unparsed)
        print
        print "=" * 80
        print

    # SEVERITY
    # Group by FATAL or ERROR severities
    for error_class in ors.values():
        # get all errors of this severity
        errors_of_class = dict(filter(
            lambda x: x[1]["severity"] == error_class,
            all_error_types.items()
        ))

        if min_date is not None:
            # only consider error_types which raised after min_date
            errors_of_class = dict(filter(
                lambda x: dt.strptime(
                    max(x[1]["timestamp"]),
                    OUTFMT
                ) > min_date,
                errors_of_class.items()
            ))
            if args.ignore_persisting:
                # ignore persisting error_types, which raised before and after
                errors_of_class = dict(filter(
                    lambda x: not (
                        dt.strptime(
                            min(x[1]["timestamp"]),
                            OUTFMT
                        ) < min_date and
                        min_date < dt.strptime(max(x[1]["timestamp"]), OUTFMT)
                    ),
                    errors_of_class.items()
                ))

        # print FATAL or ERROR heading
        if not errors_of_class:
            continue
        if errors_of_class and args.q < 4:
            print
            print error_class.upper()
            print

        # ERROR_TYPE
        for name, prototype in sorted(
            errors_of_class.items(), key=lambda x: (
                min(x[1]["timestamp"]),  # timestamp
            )
        ):

            if args.q < 4:
                # under 4, print name
                print name

                if args.q < 3:
                    # under 3, print timestamps and counts

                    if args.q < 1:
                        # under 1, print most recent raw(s) of each line number

                        # if multiple line numbers are present, print each
                        if isinstance(prototype.get("line", False), list):
                            printed = set()
                            for ts, lineno, raw in sorted(
                                zip(
                                    map(
                                        lambda s: dt.strptime(s, OUTFMT),
                                        prototype["timestamp"]
                                    ),
                                    prototype["line"],
                                    prototype["raw"]
                                ),
                                reverse=True  # sort by great-to-least
                            ):
                                # ensure only printed once
                                if lineno not in printed:
                                    # none after min_date, please
                                    if min_date is not None:
                                        if ts > min_date:
                                            print raw
                                            printed.add(lineno)
                                    else:
                                        print raw
                                        printed.add(lineno)
                        else:
                            print prototype["raw"][-1] if isinstance(
                                prototype["raw"], list
                            ) else prototype["raw"]

                    timestamps = prototype["timestamp"]
                    print "\t", max(timestamps), "-", min(timestamps)
                    print "\t", prototype["_count"], "instance{}".format(
                        "s" if prototype["_count"] else ""
                    )

                    if args.q < 2:
                        # under 2, print associations
                        print "\t{} from {}".format(
                            prototype["severity"].title(),
                            ", ".join(
                                list(set(prototype["error_file_source"]))
                            ) if isinstance(
                                prototype["error_file_source"], list
                            ) else (
                                prototype["error_file_source"]
                            )
                        )
                        if prototype["associated"]:
                            print "\t", "Associated with:"
                            for a in prototype["associated"]:
                                print "\t" * 2, a
                print

    if DEBUG:
        print prototype.keys()

    if args.output:
        json.dump(
            all_error_types,
            open(args.output, "w"),
            **JSONARGS
        )

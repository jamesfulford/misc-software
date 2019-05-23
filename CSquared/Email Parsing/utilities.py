# utilities.py

import os
import json
import re
import datetime

from css import config
from css.parsing import constants as c


#
# Utilities
#
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime(c.DATE_FORMAT)
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            return repr(o)


def datetime_parser(dct):
    # object_hook
    for k, v in dct.items():
        if isinstance(v, (unicode, str)) and re.search("\ UTC", v):
            try:
                dct[k] = datetime.datetime.strptime(v, c.DATE_FORMAT)
            except Exception:
                pass
    return dct


#
# Caching Utilities
#
def cache_records(cache_path, records):
    cache_path = os.path.join(config.DATA_DIR, cache_path)
    stash = {
        "records": records,
        "cache_time": datetime.datetime.now()
    }
    json.dump(stash, open(cache_path, "w"), cls=DateTimeEncoder)
    return stash


def retrieve_cache(relative_cachepath):
    cache = os.path.join(config.DATA_DIR, relative_cachepath)
    return json.load(open(cache), object_hook=datetime_parser)


def retrieve_records(relative_cachepath):
    return retrieve_cache(relative_cachepath)["records"]

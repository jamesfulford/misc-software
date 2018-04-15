import json
from copy import deepcopy
import hashlib
import base64


JSON_ARGS = {
    "sort_keys": True,
    "indent": 4
}


# https://stackoverflow.com/questions/5884066/hashing-a-dictionary
def make_hashable(o):
    if isinstance(o, (tuple, list)):
        return tuple((make_hashable(e) for e in o))

    if isinstance(o, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in o.items()))

    if isinstance(o, (set, frozenset)):
        return tuple(sorted(make_hashable(e) for e in o))

    return o


def send_to_hash(data):
    hasher = hashlib.md5()
    hasher.update(repr(make_hashable(data)).encode())
    return base64.b64encode(hasher.digest()).decode()


def apply_hash(record):
    record = deepcopy(record)
    if "_id" not in record:
        record["_id"] = send_to_hash(record)
    return record


class Route(object):
    def __init__(self, records):
        recs = map(apply_hash, records.values())
        self.records = dict(((r["_id"], r) for r in recs))

    def index(self):
        return self.records.values()

    def post(self, record):
        record = apply_hash(record)
        self.records[record["_id"]] = record
        self.commit()
        return record

    def get(self, requested_id):
        return self.records.get(requested_id, None)

    def put(self, requested_id, changed_fields):
        self.get(requested_id).update(changed_fields)
        self.commit()
        return self.get(requested_id)

    def commit(self):
        pass


class FileRoute(Route):
    def __init__(self, path):
        self.path = path
        Route.__init__(self, json.load(open(self.path)))

    def commit(self):
        json.dump(self.records, open(self.path, "w"), **JSON_ARGS)

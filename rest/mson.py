from bson.objectid import ObjectId
from bson.errors import InvalidId

import json
from json import JSONEncoder


def decode_id(dct):
    for key in dct:
        if isinstance(key, str) and key in ('_id', 'id', 'ids') or key.endswith('Ids') or key.endswith('Id'):
            try:
                if isinstance(dct[key], list):
                    dct[key] = [ObjectId(x) for x in dct[key]]
                elif isinstance(dct[key], str):
                    dct[key] = ObjectId(dct[key])
            except InvalidId:
                pass

    return dct


class Encoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return JSONEncoder.default(self, o)


def dumps(obj, **kw):
    return json.dumps(obj, cls=Encoder, **kw)


def loads(s, **kw):
    return json.loads(s, object_hook=decode_id, **kw)

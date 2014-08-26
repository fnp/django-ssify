import json
from .variables import SsiVariable, SsiExpect


def _json_default(o):
    if isinstance(o, SsiVariable):
        return {'__var__': o.name}
    if isinstance(o, SsiExpect):
        return {'__expect__': o.name}
    raise TypeError(o, 'not JSON serializable')


def _json_obj_hook(obj):
    if obj.keys() == ['__var__']:
        return SsiVariable(name=obj['__var__'])
    if obj.keys() == ['__expect__']:
        return SsiExpect(obj['__expect__'])
    return obj


def json_encode(obj, **kwargs):
    return json.JSONEncoder(
        default=_json_default,
        separators=(',', ':'),
        **kwargs).encode(obj)


def json_decode(data, **kwargs):
    return json.loads(data, object_hook=_json_obj_hook, **kwargs)

# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals
import json
from .variables import SsiVariable, SsiExpect


def _json_default(o):
    if isinstance(o, SsiVariable):
        return {'__var__': o.definition}
    if isinstance(o, SsiExpect):
        return {'__expect__': o.name}
    raise TypeError(o, 'not JSON serializable')


def _json_obj_hook(obj):
    keys = list(obj.keys())
    if keys == ['__var__']:
        return SsiVariable(*obj['__var__'])
    if keys == ['__expect__']:
        return SsiExpect(obj['__expect__'])
    return obj


def json_encode(obj, **kwargs):
    return json.JSONEncoder(
        default=_json_default,
        separators=(',', ':'),
        **kwargs).encode(obj)


def json_decode(data, **kwargs):
    return json.loads(data, object_hook=_json_obj_hook, **kwargs)

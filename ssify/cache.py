# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals
from django.core.cache import InvalidCacheBackendError
from .conf import conf


DEFAULT_TIMEOUT = object()


try:
    from django.core.cache import caches
except ImportError:
    from django.core.cache import get_cache
else:
    get_cache = lambda alias: caches[alias]


def get_caches():
    try:
        return [get_cache(c) for c in  conf.CACHE_ALIASES]
    except:
        try:
            return [get_cache('ssify')]
        except InvalidCacheBackendError:
            return [get_cache('default')]


def cache_include(path, content, timeout=DEFAULT_TIMEOUT, version=None):
    for cache in get_caches():
        if timeout is DEFAULT_TIMEOUT:
            cache.set(path, content, version=version)
        else:
            cache.set(path, content, timeout=timeout, version=version)


def flush_ssi_includes(paths=None):
    for cache in get_caches():
        if paths is None:
            cache.clear()
        else:
            cache.delete_many(paths)

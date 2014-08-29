# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals
from django.core.cache import get_cache
from ssify import INCLUDES_CACHES


includes_caches = [get_cache(c) for c in INCLUDES_CACHES]


def cache_include(path, content):
    for cache in includes_caches:
        cache.set(path, content)

from django.utils.cache import get_cache
from ssify import INCLUDES_CACHES


includes_caches = [get_cache(c) for c in INCLUDES_CACHES]


def cache_include(path, content):
    for cache in includes_caches:
        cache.set(path, content)

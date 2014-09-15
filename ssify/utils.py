from functools import partial
from django.utils.cache import patch_cache_control, patch_vary_headers


def ssi_cache_control(**kwargs):
    return partial(patch_cache_control, **kwargs)


def ssi_vary(newheaders):
    return partial(patch_vary_headers, newheaders=newheaders)


ssi_vary_on_cookie = ssi_vary(('Cookie',))

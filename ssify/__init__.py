"""
Implements two-phase rendering using SSI statements.

Define reqest-dependent SSI variables to use as template tags
with `ssi_variable` decorator.

Define views to be cached and included as SSI include
with `ssi_included` decorator.

"""

__version__ = '1.0'
__date__ = '2014-08-26'
__all__ = ('ssi_expect', 'SsiVariable', 'ssi_included', 'ssi_variable')

from django.conf import settings
from django.utils.functional import lazy

SETTING = lazy(
    lambda name, default: getattr(settings, name, default),
    bool, int, list, tuple, unicode)

INCLUDES_CACHES = SETTING('SSIFY_INCLUDES_CACHES', ('ssify',))
DEBUG = SETTING('SSIFY_DEBUG', False)
DEBUG_VERBOSE = SETTING('SSIFY_DEBUG_VERBOSE', True)


from .variables import ssi_expect, SsiVariable
from .decorators import ssi_included, ssi_variable

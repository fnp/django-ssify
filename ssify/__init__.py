# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
"""
Implements two-phase rendering using SSI statements.

Define reqest-dependent SSI variables to use as template tags
with `ssi_variable` decorator.

Define views to be cached and included as SSI include
with `ssi_included` decorator.

"""
from __future__ import unicode_literals

__version__ = '1.0'
__date__ = '2014-08-26'
__all__ = ('flush_ssi_includes', 'ssi_expect', 'SsiVariable', 'ssi_included', 'ssi_variable')

from .variables import ssi_expect, SsiVariable
from .decorators import ssi_included, ssi_variable
from .cache import flush_ssi_includes

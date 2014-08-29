# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
"""
This file works only for django.test.simple.DjangoTestSuiteRunner
in Django<1.6.  The newer django.test.runner.DiscoverRunner finds
test_* modules by itself.

"""
from __future__ import unicode_literals

from .test_args import *
from .test_basic import *
from .test_csrf import *
from .test_locale import *
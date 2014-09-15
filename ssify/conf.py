# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from django.conf import settings


class AppSettings(object):
    prefix = 'SSIFY_'

    @classmethod
    def add(cls, name, default):
        setattr(cls, name, property(lambda self:
            getattr(settings, self.prefix + name, default)))


AppSettings.add('CACHE_ALIASES', None)
AppSettings.add('RENDER', False)
AppSettings.add('RENDER_VERBOSE', False)


conf = AppSettings()

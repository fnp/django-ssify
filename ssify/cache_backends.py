# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals
import os
from django.core.cache.backends.filebased import FileBasedCache


class StaticFileBasedCache(FileBasedCache):
    def __init__(self, *args, **kwargs):
        super(StaticFileBasedCache, self).__init__(*args, **kwargs)
        self._dir = os.path.abspath(self._dir)

    def make_key(self, key, version=None):
        assert version is None, \
            'StaticFileBasedCache does not support versioning.'
        return key

    def _key_to_file(self, key):
        key = os.path.abspath(os.path.join(self._dir, key.lstrip('/')))
        assert key.startswith(self._dir), 'Trying to save path outside root.'
        if key.endswith('/'):
            key += 'index.html'
        return key

    def get(self, key, default=None, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        fname = self._key_to_file(key)
        try:
            with open(fname, 'rb') as inf:
                return inf.read()
        except (IOError, OSError):
            pass
        return default

    def set(self, key, value, timeout=None, version=None):
        assert timeout is None, \
            'StaticFileBasedCache does not support timeouts.'
        key = self.make_key(key, version=version)
        self.validate_key(key)
        fname = self._key_to_file(key)
        dirname = os.path.dirname(fname)
        try:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            with open(fname, 'wb') as outf:
                outf.write(value)
        except (IOError, OSError):
            pass

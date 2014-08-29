# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals

import re


splitter = re.compile(br'(?<=-->)\s*(?=<!--#)')

def split_ssi(ssi_text):
    """re.split won't split on empty sequence, so we need that."""
    ssi_text = ssi_text.strip()
    start = 0
    for match in re.finditer(splitter, ssi_text):
        yield ssi_text[start:match.start()]
        start = match.end()
    yield ssi_text[start:]

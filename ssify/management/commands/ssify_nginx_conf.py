# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals
from optparse import make_option
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
    )
    help = 'Dumps configuration for NGINX.'

    def handle(self, **options):
        pass

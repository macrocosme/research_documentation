# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class alertWebConfig(AppConfig):
    name = 'alert_web'

    def ready(self):
        import alert_web.signals

"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from alert_web import models


class GalaxyResource(ModelResource):
    class Meta:
        model = models.Galaxy


class GalaxyAdmin(ImportExportModelAdmin):
    resource_class = GalaxyResource


# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Verification)
admin.site.register(models.ImageStore)
admin.site.register(models.Survey)
admin.site.register(models.SurveyElement)
admin.site.register(models.SurveyQuestion)
admin.site.register(models.Question)
admin.site.register(models.QuestionOption)
admin.site.register(models.Response)
admin.site.register(models.QuestionResponse)
admin.site.register(models.QuestionDrawnResponse)
admin.site.register(models.Galaxy, GalaxyAdmin)

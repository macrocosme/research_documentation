"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from django.contrib import admin

from alert_celery import models


@admin.register(models.SurveyGeneration)
class SurveyGeneration(admin.ModelAdmin):
    list_display = ('requester', 'request_date', 'status', 'execution_date', 'survey', 'comments', )


@admin.register(models.SurveyObjectGeneration)
class SurveyObjectGeneration(admin.ModelAdmin):
    list_display = ('requester', 'request_date', 'status', 'execution_date', 'survey', 'comments', )

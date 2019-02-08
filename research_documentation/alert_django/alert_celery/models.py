"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from django.db import models

from alert_web.models import User, Survey


class SurveyGeneration(models.Model):
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'
    FAILED = 'Failed'

    STATUS_CHOICES = (
        (IN_PROGRESS, IN_PROGRESS),
        (COMPLETED, COMPLETED),
        (FAILED, FAILED),
    )

    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS)
    execution_date = models.DateTimeField(null=True, blank=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)


class SurveyObjectGeneration(models.Model):
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'
    FAILED = 'Failed'

    STATUS_CHOICES = (
        (IN_PROGRESS, IN_PROGRESS),
        (COMPLETED, COMPLETED),
        (FAILED, FAILED),
    )

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, null=False, blank=False)
    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS)
    execution_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

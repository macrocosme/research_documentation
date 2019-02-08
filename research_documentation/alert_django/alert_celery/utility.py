"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from alert_celery.models import SurveyGeneration, SurveyObjectGeneration


def survey_generation_in_progress():
    return SurveyGeneration.objects.filter(status=SurveyGeneration.IN_PROGRESS).exists()


def add_more_objects_to_survey_in_progress(survey):
    return SurveyObjectGeneration.objects.filter(survey=survey, status=SurveyObjectGeneration.IN_PROGRESS).exists()

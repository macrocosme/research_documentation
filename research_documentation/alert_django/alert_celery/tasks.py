"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.utils import timezone

from alert_web.utility.survey import generate_new_survey, generate_recommendations_for_survey
from alert_web.mailer.actions import email_survey_created, email_survey_failed

from alert_celery.models import SurveyGeneration, SurveyObjectGeneration
from alert_web.models import User, Survey


@shared_task
def generate_survey_and_email(email, title, first_name, last_name, username):
    failure_reason = 'Something went wrong while generating the survey.'

    # make a new entry to the database
    survey_generation = SurveyGeneration.objects.create(
        requester=User.objects.get(username=username),
    )

    try:
        survey_created = generate_new_survey()
        survey_generation.status = SurveyGeneration.COMPLETED
        survey_generation.execution_date = timezone.now()
        survey_generation.survey = survey_created
        survey_generation.save()
    except:
        survey_created = None
        survey_generation.status = SurveyGeneration.FAILED
        survey_generation.execution_date = timezone.now()
        survey_generation.comments = failure_reason
        survey_generation.save()

    # sending email to the requester
    failure_reason += ' Please try again. If the problem keeps on occuring, please contact your system administrator.'

    if survey_created:
        email_survey_created(
            to_addresses=[email, ],
            title=title,
            first_name=first_name,
            last_name=last_name,
            creation_date=survey_created.creation_date.date(),
        )
    else:
        email_survey_failed(
            to_addresses=[email, ],
            title=title,
            first_name=first_name,
            last_name=last_name,
            failure_reason=failure_reason,
        )


@shared_task
def add_more_survey_objects(survey_id, username):
    failure_reason = 'Something went wrong while adding more recommendations to survey.'

    survey = Survey.objects.get(id=survey_id)

    survey_object_generation = SurveyObjectGeneration.objects.create(
        requester=User.objects.get(username=username),
        survey=survey,
    )

    try:
        generate_recommendations_for_survey(survey=survey)

        # update survey object generation status
        survey_object_generation.status = SurveyObjectGeneration.COMPLETED
        survey_object_generation.execution_date = timezone.now()
        survey_object_generation.save()
    except:
        survey_object_generation.status = SurveyObjectGeneration.FAILED
        survey_object_generation.execution_date = timezone.now()
        survey_object_generation.comments = failure_reason
        survey_object_generation.save()

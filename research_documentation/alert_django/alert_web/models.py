"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import uuid
import django.contrib.auth.models as auth_models

from django.db import models
from django_countries.fields import CountryField

from alert_web.utility import constants

logger = logging.getLogger(__name__)


class User(auth_models.AbstractUser):
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    NOT_DISCLOSED = ''
    MR = 'Mr'
    MS = 'Ms'
    MRS = 'Mrs'
    DR = 'Dr'
    PROF = 'Prof'
    A_PROF = 'A/Prof'

    TITLE_CHOICES = [
        (NOT_DISCLOSED, NOT_DISCLOSED),
        (MR, MR),
        (MS, MS),
        (MRS, MRS),
        (DR, DR),
        (PROF, PROF),
        (A_PROF, A_PROF),
    ]

    MALE = 'Male'
    FEMALE = 'Female'
    GENDER_CHOICES = [
        (NOT_DISCLOSED, NOT_DISCLOSED),
        (FEMALE, FEMALE),
        (MALE, MALE),
    ]

    title = models.CharField(max_length=10, choices=TITLE_CHOICES, default=NOT_DISCLOSED, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default=NOT_DISCLOSED, blank=True)
    is_student = models.BooleanField(default=False)
    institution = models.CharField(max_length=100)
    country = CountryField(blank_label='Select Country', null=False, blank=False)
    scientific_interests = models.TextField(verbose_name='Scientific Interests', blank=True, null=True)

    UNVERIFIED = 'Unverified'
    VERIFIED = 'Verified'
    CONFIRMED = 'Confirmed'
    DELETED = 'Deleted'
    STATUS_CHOICES = [
        (UNVERIFIED, 'Unverified'),
        (VERIFIED, 'Verified'),
        (CONFIRMED, 'Confirmed'),
        (DELETED, 'Deleted'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=False, default=UNVERIFIED)

    def __unicode__(self):
        return u'%s %s %s (%s)' % (self.title, self.first_name, self.last_name, self.username)

    def __str__(self):
        return u'%s %s %s (%s)' % (self.title, self.first_name, self.last_name, self.username)

    def as_json(self):
        return dict(
            user=self,
            id=self.id,
            value=dict(
                username=self.username,
                title=self.title,
                first_name=self.first_name,
                last_name=self.last_name,
            ),
        )


class Galaxy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first = models.TextField(null=False, blank=False)
    sdss = models.TextField(null=True, blank=True)
    ra = models.TextField(null=False, blank=False)
    dec = models.TextField(null=False, blank=False)
    fint = models.FloatField(null=False, blank=False)
    fpeak = models.FloatField(null=False, blank=False)
    rms = models.FloatField(null=False, blank=False)
    maj = models.FloatField(null=False, blank=False)
    min = models.FloatField(null=False, blank=False)
    pa = models.FloatField(null=False, blank=False)
    index = models.IntegerField(null=False, blank=False)
    my_label = models.TextField(null=True, blank=True)

    nn2 = models.IntegerField(null=False, blank=False)
    nn2_first = models.TextField(null=True, blank=True)
    nn2_angle = models.FloatField(null=False, blank=False)
    nn2_fint = models.FloatField(null=False, blank=False)
    nn2_fpeak = models.FloatField(null=False, blank=False)
    nn2_rms = models.FloatField(null=False, blank=False)
    nn2_maj = models.FloatField(null=False, blank=False)
    nn2_min = models.FloatField(null=False, blank=False)

    nn3 = models.IntegerField(null=False, blank=False)
    nn3_first = models.TextField(null=True, blank=True)
    nn3_angle = models.FloatField(null=False, blank=False)
    nn3_fint = models.FloatField(null=False, blank=False)
    nn3_fpeak = models.FloatField(null=False, blank=False)
    nn3_rms = models.FloatField(null=False, blank=False)
    nn3_maj = models.FloatField(null=False, blank=False)
    nn3_min = models.FloatField(null=False, blank=False)

    nn4 = models.IntegerField(null=False, blank=False)
    nn4_first = models.TextField(null=True, blank=True)
    nn4_angle = models.FloatField(null=False, blank=False)
    nn4_fint = models.FloatField(null=False, blank=False)
    nn4_fpeak = models.FloatField(null=False, blank=False)
    nn4_rms = models.FloatField(null=False, blank=False)
    nn4_maj = models.FloatField(null=False, blank=False)
    nn4_min = models.FloatField(null=False, blank=False)

    nn5 = models.IntegerField(null=False, blank=False)
    nn5_first = models.TextField(null=True, blank=True)
    nn5_angle = models.FloatField(null=False, blank=False)
    nn5_fint = models.FloatField(null=False, blank=False)
    nn5_fpeak = models.FloatField(null=False, blank=False)
    nn5_rms = models.FloatField(null=False, blank=False)
    nn5_maj = models.FloatField(null=False, blank=False)
    nn5_min = models.FloatField(null=False, blank=False)

    nn6 = models.IntegerField(null=False, blank=False)
    nn6_first = models.TextField(null=True, blank=True)
    nn6_angle = models.FloatField(null=False, blank=False)
    nn6_fint = models.FloatField(null=False, blank=False)
    nn6_fpeak = models.FloatField(null=False, blank=False)
    nn6_rms = models.FloatField(null=False, blank=False)
    nn6_maj = models.FloatField(null=False, blank=False)
    nn6_min = models.FloatField(null=False, blank=False)

    nn7 = models.IntegerField(null=False, blank=False)
    nn7_first = models.TextField(null=True, blank=True)
    nn7_angle = models.FloatField(null=False, blank=False)
    nn7_fint = models.FloatField(null=False, blank=False)
    nn7_fpeak = models.FloatField(null=False, blank=False)
    nn7_rms = models.FloatField(null=False, blank=False)
    nn7_maj = models.FloatField(null=False, blank=False)
    nn7_min = models.FloatField(null=False, blank=False)

    def __unicode__(self):
        return u'%s' % self.first

    def __str__(self):
        return u'%s' % self.first

    def as_json(self):
        return dict(
            id=self.id,
            first=self.first,
            sdss=self.sdss,
            ra=self.ra,
            dec=self.dec,
            fint=self.fint,
            fpeak=self.fpeak,
            rms=self.rms,
            maj=self.maj,
            min=self.min,
            pa=self.pa,
            index=self.index,
            my_label=self.my_label,
            n2=self.nn2,
            nn2_first=self.nn2_first,
            nn2_angle=self.nn2_angle,
            nn2_fint=self.nn2_fint,
            nn2_fpeak=self.nn2_fpeak,
            nn2_rms=self.nn2_rms,
            nn2_maj=self.nn2_maj,
            nn2_min=self.nn2_min,
            nn3=self.nn3,
            nn3_first=self.nn3_first,
            nn3_angle=self.nn3_angle,
            nn3_fint=self.nn3_fint,
            nn3_fpeak=self.nn3_fpeak,
            nn3_rms=self.nn3_rms,
            nn3_maj=self.nn3_maj,
            nn3_min=self.nn3_min,
            nn4=self.nn4,
            nn4_first=self.nn4_first,
            nn4_angle=self.nn4_angle,
            nn4_fint=self.nn4_fint,
            nn4_fpeak=self.nn4_fpeak,
            nn4_rms=self.nn4_rms,
            nn4_maj=self.nn4_maj,
            nn4_min=self.nn4_min,
            nn5=self.nn5,
            nn5_first=self.nn5_first,
            nn5_angle=self.nn5_angle,
            nn5_fint=self.nn5_fint,
            nn5_fpeak=self.nn5_fpeak,
            nn5_rms=self.nn5_rms,
            nn5_maj=self.nn5_maj,
            nn5_min=self.nn5_min,
            nn6=self.nn6,
            nn6_first=self.nn6_first,
            nn6_angle=self.nn6_angle,
            nn6_fint=self.nn6_fint,
            nn6_fpeak=self.nn6_fpeak,
            nn6_rms=self.nn6_rms,
            nn6_maj=self.nn6_maj,
            nn6_min=self.nn6_min,
            nn7=self.nn7,
            nn7_first=self.nn7_first,
            nn7_angle=self.nn7_angle,
            nn7_fint=self.nn7_fint,
            nn7_fpeak=self.nn7_fpeak,
            nn7_rms=self.nn7_rms,
            nn7_maj=self.nn7_maj,
            nn7_min=self.nn7_min
        )


class ImageStore(models.Model):
    TGSS = constants.TGSS
    FIRST = constants.FIRST
    DATABASE_CHOICES = [
        (TGSS, TGSS),
        (FIRST, FIRST),
    ]

    galaxy = models.ForeignKey(Galaxy, on_delete=models.CASCADE)
    database_type = models.CharField(max_length=10, choices=DATABASE_CHOICES, blank=False, null=False)
    image = models.TextField(null=True, blank=True)
    actual_url = models.TextField(null=False, blank=False)

    class Meta:
        unique_together = ("galaxy", "database_type")

    def __unicode__(self):
        return u'(%s, %s) %s' % (self.galaxy.ra, self.galaxy.dec, self.database_type,)

    def __str__(self):
        return u'(%s, %s) %s' % (self.galaxy.ra, self.galaxy.dec, self.database_type,)


class Question(models.Model):
    RADIO = 'radio'
    SELECT = 'select'
    TEXT = 'text'
    NUMBER = 'number'
    question_categories = (
        (RADIO, RADIO),
        (SELECT, SELECT),
        (TEXT, TEXT),
        (NUMBER, NUMBER),
    )
    text = models.TextField(null=False, blank=False)
    category = models.CharField(max_length=10, choices=question_categories, default=None, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return u'[%s] %s (%s)' % (self.category, self.text, 'Active' if self.active else 'Inactive',)

    def __str__(self):
        return u'[%s] %s (%s)' % (self.category, self.text, 'Active' if self.active else 'Inactive',)


class QuestionOption(models.Model):
    option = models.CharField(max_length=100, blank=False, null=False, unique=True)
    option_label = models.CharField(max_length=10, blank=False, null=False, unique=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_default_option = models.BooleanField(default=False)

    def __unicode__(self):
        return u'[%s] %s' % (self.option, self.question.text,)

    def __str__(self):
        return u'[%s] %s' % (self.option, self.question.text,)


class SurveyElement(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    galaxy = models.ForeignKey(Galaxy, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('question', 'galaxy')

    def __unicode__(self):
        return u'(%s, %s) %s' % (self.galaxy.ra, self.galaxy.dec, self.question.text,)

    def __str__(self):
        return u'(%s, %s) %s' % (self.galaxy.ra, self.galaxy.dec, self.question.text,)


class Survey(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s (%s) [%s]' % (self.id, self.creation_date, 'Active' if self.active else 'Inactive',)

    def __str__(self):
        return u'%s (%s) [%s]' % (self.id, self.creation_date, 'Active' if self.active else 'Inactive',)


class SurveyQuestion(models.Model):
    survey_element = models.ForeignKey(SurveyElement, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    def __unicode__(self):
        return u'[%s] %s' % (self.survey.id, self.survey_element,)

    def __str__(self):
        return u'[%s] %s' % (self.survey.id, self.survey_element,)


class Response(models.Model):
    ACTIVE = 'Active'
    FINISHED = 'Finished'
    PROCESSED = 'Processed'  # Will be used to teach Acton

    STATUS_CHOICES = (
        (ACTIVE, ACTIVE),
        (FINISHED, FINISHED),
        (PROCESSED, PROCESSED),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE, null=False, blank=False)

    class Meta:
        unique_together = ("user", "survey")

    def __unicode__(self):
        return u'%s - Survey id: %s :: Status: [%s]' % (self.user, self.survey.id, self.status)

    def __str__(self):
        return u'%s - Survey id: %s :: Status: [%s]' % (self.user, self.survey.id, self.status)


class QuestionResponse(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    survey_question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    answer = models.TextField()
    comments = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("response", "survey_question")

    def __unicode__(self):
        return u'%s - %s - %s' % (self.response.id, self.survey_question, self.answer)

    def __str__(self):
        return u'%s - %s - %s' % (self.response.id, self.survey_question, self.answer)


class QuestionDrawnResponse(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    survey_question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    x_coordinates = models.TextField()
    y_coordinates = models.TextField()

    class Meta:
        unique_together = ("response", "survey_question")

    def __unicode__(self):
        return u'%s - %s' % (self.response.id, self.survey_question)

    def __str__(self):
        return u'%s - %s' % (self.response.id, self.survey_question)


class Verification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    information = models.CharField(max_length=1024)
    expiry = models.DateTimeField(null=True)
    verified = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s' % self.information

    def __str__(self):
        return u'%s' % self.information

"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from django.db import migrations, models


def add_question_and_options(apps, schema_editor):
    from alert_web.models import Question, QuestionOption

    question = Question(
        text='What kind of galaxy is this?',
        category=Question.RADIO
    )
    question.save()

    QuestionOption(
        question=question,
        option='FR-I',
        option_label='I'
    ).save()

    QuestionOption(
        question=question,
        option='FR-II',
        option_label='II'
    ).save()

    QuestionOption(
        question=question,
        option='Unknown',
        option_label='B'
    ).save()


def upload_data(apps, schema_editor):
    from alert_web.models import Galaxy
    from pandas import read_csv
    from django.conf import settings

    galaxies = read_csv(settings.BASE_DIR + '/../alert_web/static/fri_frii_background_features.csv')

    for galaxy in galaxies.itertuples():
        Galaxy.objects.create(
            first=galaxy.first,
            sdss=galaxy.sdss,
            ra=galaxy.ra,
            dec=galaxy.dec,
            fint=galaxy.fint,
            fpeak=galaxy.fpeak,
            rms=galaxy.rms,
            maj=galaxy.maj,
            min=galaxy.min,
            pa=galaxy.pa,
            index=galaxy.index,
            my_label=galaxy.my_label,
            nn2=galaxy.nn2,
            nn2_first=galaxy.nn2_first,
            nn2_angle=galaxy.nn2_angle,
            nn2_fint=galaxy.nn2_fint,
            nn2_fpeak=galaxy.nn2_fpeak,
            nn2_rms=galaxy.nn2_rms,
            nn2_maj=galaxy.nn2_maj,
            nn2_min=galaxy.nn2_min,
            nn3=galaxy.nn3,
            nn3_first=galaxy.nn3_first,
            nn3_angle=galaxy.nn3_angle,
            nn3_fint=galaxy.nn3_fint,
            nn3_fpeak=galaxy.nn3_fpeak,
            nn3_rms=galaxy.nn3_rms,
            nn3_maj=galaxy.nn3_maj,
            nn3_min=galaxy.nn3_min,
            nn4=galaxy.nn4,
            nn4_first=galaxy.nn4_first,
            nn4_angle=galaxy.nn4_angle,
            nn4_fint=galaxy.nn4_fint,
            nn4_fpeak=galaxy.nn4_fpeak,
            nn4_rms=galaxy.nn4_rms,
            nn4_maj=galaxy.nn4_maj,
            nn4_min=galaxy.nn4_min,
            nn5=galaxy.nn5,
            nn5_first=galaxy.nn5_first,
            nn5_angle=galaxy.nn5_angle,
            nn5_fint=galaxy.nn5_fint,
            nn5_fpeak=galaxy.nn5_fpeak,
            nn5_rms=galaxy.nn5_rms,
            nn5_maj=galaxy.nn5_maj,
            nn5_min=galaxy.nn5_min,
            nn6=galaxy.nn6,
            nn6_first=galaxy.nn6_first,
            nn6_angle=galaxy.nn6_angle,
            nn6_fint=galaxy.nn6_fint,
            nn6_fpeak=galaxy.nn6_fpeak,
            nn6_rms=galaxy.nn6_rms,
            nn6_maj=galaxy.nn6_maj,
            nn6_min=galaxy.nn6_min,
            nn7=galaxy.nn7,
            nn7_first=galaxy.nn7_first,
            nn7_angle=galaxy.nn7_angle,
            nn7_fint=galaxy.nn7_fint,
            nn7_fpeak=galaxy.nn7_fpeak,
            nn7_rms=galaxy.nn7_rms,
            nn7_maj=galaxy.nn7_maj,
            nn7_min=galaxy.nn7_min,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('alert_web', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_question_and_options),
        migrations.RunPython(upload_data),
    ]

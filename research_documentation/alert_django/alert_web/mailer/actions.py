"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from __future__ import unicode_literals

from alert_web.mailer import templates, email


def email_verify_request(to_addresses, title, first_name, last_name, link):
    context = {
        'title': title,
        'first_name': first_name,
        'last_name': last_name,
        'link': link,
    }

    email.Email(
        subject=templates.VERIFY_EMAIL_ADDRESS['subject'],
        to_addresses=to_addresses,
        template=templates.VERIFY_EMAIL_ADDRESS['message'],
        context=context,
    ).send_email()


def email_survey_created(to_addresses, title, first_name, last_name, creation_date):
    context = {
        'title': title,
        'first_name': first_name,
        'last_name': last_name,
        'creation_date': creation_date,
    }

    email.Email(
        subject=templates.SURVEY_CREATED['subject'],
        to_addresses=to_addresses,
        template=templates.SURVEY_CREATED['message'],
        context=context,
    ).send_email()


def email_survey_failed(to_addresses, title, first_name, last_name, failure_reason):
    context = {
        'title': title,
        'first_name': first_name,
        'last_name': last_name,
        'failure_reason': failure_reason,
    }

    email.Email(
        subject=templates.SURVEY_CREATION_FAILED['subject'],
        to_addresses=to_addresses,
        template=templates.SURVEY_CREATION_FAILED['message'],
        context=context,
    ).send_email()

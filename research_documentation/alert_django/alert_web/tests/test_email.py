"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from __future__ import unicode_literals

from django.test import TestCase
from django.core import mail

from alert_web.mailer.email import Email


class TestEmail(TestCase):

    def test_email(self):  # tests whether an email can be sent
        subject = 'Test Subject'
        to_addresses = ['testto@localhost.com']
        context = {
            'message': 'message',
        }
        template = '<p>hi,</p><p>This is {{message}}</p>'
        from_address = 'testfrom@localhost.com'
        email = Email(subject, to_addresses, template, context, from_address=from_address)
        email.send_email()
        self.assertEqual([(x.to, x.body) for x in mail.outbox], [(['testto@localhost.com', ], 'hi,This is message')])

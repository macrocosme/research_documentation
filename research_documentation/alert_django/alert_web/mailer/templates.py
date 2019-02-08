"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

VERIFY_EMAIL_ADDRESS = dict()
VERIFY_EMAIL_ADDRESS['subject'] = '[alert] Please verify your email address'
VERIFY_EMAIL_ADDRESS['message'] = '<p>Dear {{title}} {{first_name}} {{last_name}}</p>' \
                                  '<p>We have received a new account request with our alert system from this' \
                                  'email address. Please verify your email address by clicking on the following ' \
                                  '<a href="{{link}}" target="_blank">link</a>:</p>' \
                                  '<p><a href="{{link}}" target="_blank">{{link}}</a></p>' \
                                  '<p>If you believe that the email has been sent by mistake or you have not ' \
                                  'requested for an account please <strong>do not</strong> click on the link.</p>' \
                                  '<p>Alternatively you can report this incident to <a ' \
                                  'href="mailto:support@alert.com" target="_top">support@alert.com</a> for ' \
                                  'investigation.</p>' \
                                  '<p>&nbsp;</p>' \
                                  '<p>Regards,</p>' \
                                  '<p>alert Team</p>'

SURVEY_CREATED = dict()
SURVEY_CREATED['subject'] = '[alert] New Survey Created'
SURVEY_CREATED['message'] = '<p>Dear {{title}} {{first_name}} {{last_name}}</p>' \
                            '<p>A new survey has been created as per your request on {{creation_date}}.</p>' \
                            '<p>Now the users will be able to access it for classification.</p>' \
                            '<p>&nbsp;</p>' \
                            '<p>Regards,</p>' \
                            '<p>alert Team</p>'

SURVEY_CREATION_FAILED = dict()
SURVEY_CREATION_FAILED['subject'] = '[alert] New Survey Creation Failed'
SURVEY_CREATION_FAILED['message'] = '<p>Dear {{title}} {{first_name}} {{last_name}}</p>' \
                                    '<p>You have requested for a new survey on {{creation_date}}.</p>' \
                                    '<p>Unfortunately the survey creation could not be done due to the following:</p>' \
                                    '<p>{{failure_reason}}</p>' \
                                    '<p>&nbsp;</p>' \
                                    '<p>Regards,</p>' \
                                    '<p>alert Team</p>'

"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from .base import *

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = 'mail.swin.edu.au'
EMAIL_PORT = 25

try:
    from .local import *
except ImportError:
    pass

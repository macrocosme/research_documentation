"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from django.shortcuts import render
from six.moves.urllib import parse

from alert_web.models import User
from alert_web.utility import utils


def verify(request):
    """Verify an account.

    Parameters
    ----------
    request:
        POST request

    Returns
    -------
    render:
        django.shortcuts.render (a page to be rendered)
    """
    data = {}
    code_encrypted = request.GET.get('verification_code', None)
    if code_encrypted:
        try:
            code = utils.get_information(code_encrypted)
            params = dict(parse.parse_qsl(code))
            verify_type = params.get('type', None)
            if verify_type == 'user':
                username = params.get('username', None)
                try:
                    user = User.objects.get(username=username)
                    user.status = user.VERIFIED
                    user.is_active = True
                    user.save()
                    data.update(
                        success=True,
                        message='The email address has been verified successfully',
                    )
                except User.DoesNotExist:
                    data.update(
                        success=False,
                        message='The requested user account to verify does not exist',
                    )
        except ValueError as e:
            # This may be a variant between versions...
            try:
                data.update(
                    success=False,
                    message=e.message if e.message else 'Invalid verification code',
                )
            except:
                data.update(
                    success=False,
                    message=e if e else 'Invalid verification code',
                )
    else:
        data.update(
            success=False,
            message='Invalid Verification Code',
        )
    return render(
        request,
        "accounts/notification.html",
        {
            'type': 'email_verify',
            'data': data,
        },
    )

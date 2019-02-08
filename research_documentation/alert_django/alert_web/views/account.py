"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from __future__ import unicode_literals

import warnings
import functools

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator

from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.deprecation import (
    RemovedInDjango20Warning, RemovedInDjango21Warning,
)
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache

from alert_web.forms.account.registration import RegistrationForm
from alert_web.forms.account.profile import (
    EditProfileForm, PasswordChangeForm, SetPasswordForm,
)
from alert_web.mailer.actions import email_verify_request
from alert_web.utility import constants
from alert_web.utility.utils import get_absolute_site_url, get_token

from django.utils.translation import ugettext_lazy as _

UserModel = get_user_model()


def registration(request):
    """Register a user.

    Parameters
    ----------
    request:
        POST request

    Returns
    -------
    render:
        django.shortcuts.render (page to be rendered)
    """
    data = {}
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            form.save()

            # generating verification link
            verification_link = get_absolute_site_url(request) + \
                                '/verify?verification_code=' + \
                                get_token(
                                    information='type=user&username={}'.format(data.get('username')),
                                    validity=constants.EMAIL_VERIFY_EXPIRY,
                                )

            # Sending email to the potential user to verify the email address
            email_verify_request(
                to_addresses=[data.get('email')],
                title=data.get('title'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                link=verification_link,
            )

            return render(
                request,
                "accounts/notification.html",
                {
                    'type': 'registration_submitted',
                    'data': data,
                },
            )
    else:
        form = RegistrationForm()

    return render(
        request,
        "accounts/registration.html",
        {
            'form': form,
            'data': data,
            'submit_text': 'Register',
        },
    )


@login_required
def profile(request):
    """Profile view

    Parameters
    ----------
    request:
        GET or POST request

    Returns
    -------
    render:
         django.shortcuts.render (a page to be rendered)
    """
    data = {}
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            data = form.cleaned_data
            form.save()
            messages.success(request, 'Informations successfully updated', 'alert alert-success')
            return render(
                request,
                "accounts/profile.html",
                {
                    'form': form,
                    'type': 'update_profile_success',
                    'data': data,
                },
            )
        else:
            messages.error(request, 'Please correct the error(s) below.', 'alert alert-warning')
    else:
        form = EditProfileForm(instance=request.user)

    return render(
        request,
        "accounts/profile.html",
        {
            'form': form,
            'data': data,
            'submit_text': 'Update',
        },
    )


@login_required
def change_password(request):
    """Change a user password.

    Parameters
    ----------
    request:
        GET or POST request

    Returns
    -------
    render
        django.shortcuts.render (a page to be rendered)
    """

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been successfully updated', 'alert alert-success')
            return redirect('change_password')
            # else:
            #     # messages.error(request, 'Please correct the error below.')
            #     messages.error(request, 'Please correct the error below.', 'alert alert-warning')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })


# ************************************************************************************
#
# Reset password Section
#
# ************************************************************************************
def deprecate_current_app(func):
    """Handle deprecation of the current_app parameter of the views.
    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
        if 'current_app' in kwargs:
            warnings.warn(
                "Passing `current_app` as a keyword argument is deprecated. "
                "Instead the caller of `{0}` should set "
                "`request.current_app`.".format(func.__name__),
                RemovedInDjango20Warning
            )
            current_app = kwargs.pop('current_app')
            request = kwargs.get('request', None)
            if request and current_app is not None:
                request.current_app = current_app
        return func(*args, **kwargs)

    return inner


# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
@deprecate_current_app
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    warnings.warn("The password_reset_confirm() view is superseded by the "
                  "class-based PasswordResetConfirmView().",
                  RemovedInDjango21Warning, stacklevel=2)
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        title = _('Enter new password')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = _('Password reset unsuccessful')
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)

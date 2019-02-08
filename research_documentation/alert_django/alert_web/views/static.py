"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from __future__ import unicode_literals

from django.shortcuts import render


def index(request):
    return render(
        request,
        "base/welcome.html",
    )


def about(request):
    return render(
        request,
        "about/about.html",
    )

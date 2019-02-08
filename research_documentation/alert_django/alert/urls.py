"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('alert_web.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

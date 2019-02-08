"""
Distributed under the MIT License. See LICENSE.txt for more info.
"""

from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from alert_web.views import account, static, verify, classify, administration

urlpatterns = [
    url(r'^$', static.index, name='index'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^register/$', account.registration, name='register'),
    url(r'^verify/$', verify.verify, name='verify'),

    url(r'^about/$', static.about, name='about'),
    url(r'^administration/$', administration.administration, name='administration'),
    url(r'^classify/$', classify.classify, name='classify'),

    url(r'^accounts/login/$',
        auth_views.LoginView.as_view(redirect_authenticated_user=True,
                                     template_name='accounts/login.html'), name='login'),
    url(r'^accounts/logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^accounts/profile/$', account.profile, name='profile'),
    url(r'^accounts/password/$', account.change_password, name='change_password'),

    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        account.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),

]

from django.contrib.auth.views import (
    LogoutView,
    LoginView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView)

from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view(template_name='users/password_change_form.html'),
        name='change_pass'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
        name='change_done'
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(),
        name='reset_pass'
    ),
]

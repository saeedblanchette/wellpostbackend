"""willpostbackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import AllowAny
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView
from willpost.views import ContactDetailView, ServeMedia,PostView,ContactListView, ExistenceConfirmationView, UserDetailsView, TwoFactorAuthConfirm, EmailTwoFactorAuthSendView, CLoginView, MediaListView, MediaDetailView, VoteView
from dj_rest_auth.registration.views import VerifyEmailView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    # Authentication system
    path('dj-rest-auth/login/', CLoginView.as_view()),
    path('dj-rest-auth/user/', UserDetailsView.as_view()),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('auth/confirm/<uid>/<token>/',

         TwoFactorAuthConfirm, name='email_twofactor_auth_confirm'),
    path('auth/confirm/send/',

         EmailTwoFactorAuthSendView.as_view(), name='twofactor_auth_send'),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('account-confirm-email/', VerifyEmailView.as_view(),
         name='account_email_verification_sent'),
    path('password-reset/confirm/<uidb64>/<token>/',
         TemplateView.as_view(), name='password_reset_confirm'),
    # contact
    path('contact/', ContactListView.as_view()),
    path('contact/<pk>', ContactDetailView.as_view()),
    # media
    path("media/", MediaListView.as_view()),
    path("media/<pk>", MediaDetailView.as_view()),
    # post
    path("post/<urlsignature>", PostView.as_view()),
    # confirmation ,
    path("confirmation/exc/",
         ExistenceConfirmationView.as_view()),
    # vote
    path("vote/<urlsignature>", VoteView.as_view()),
    path("vote/", VoteView.as_view()),
    # API documenting
    path('openapi', get_schema_view(
        title="Your Project",
        description="API for all things …",
        version="1.0.0",
        public=True,
        permission_classes=[AllowAny]
    ), name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',

        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
    path('admin/', admin.site.urls),





]
# if settings.DEBUG:

#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)

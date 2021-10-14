import base64
from datetime import timedelta
import urllib
from django.utils import timezone
from willpostbackend.settings import DEFAULT_FROM_EMAIL
# from django.contrib.auth.tokens import default_token_generator
from allauth.account.forms import default_token_generator
from dj_rest_auth.serializers import LoginSerializer as DefaultLoginSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
from django.conf import settings
from dj_rest_auth.registration.serializers import RegisterSerializer as DefaultRegisterSerializer
from django.contrib.auth.forms import PasswordResetForm
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework import fields, serializers
from willpost import models
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from allauth.account.models import EmailAddress
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired
from willpost.utils import get_client_ip
import hashlib
import calendar
import time
# Get the UserModel
UserModel = get_user_model()


class SecuredFilePathSerializer(serializers.FileField):
    def to_representation(self, value):
        new_value = super().to_representation(value)
        request = self.context.get('request', None)
        _ip_addr = get_client_ip(request)
        media_url = getattr(settings, 'MEDIA_URL')
        path = media_url + value.name
        target_time = timezone.now()+timedelta(days=1)
        exp_time = calendar.timegm(target_time.timetuple())
        str2hash = str(exp_time)+path+_ip_addr+' enigma'
        hash = base64.urlsafe_b64encode(hashlib.md5(
            str2hash.encode()).digest()).decode('utf-8').replace('=', '')
        query_dict = {'token': hash, 'expires': exp_time}
        from urllib.parse import urlencode
        path_with_query = f'{path}?{urlencode(query_dict)}'
        if request is not None:
            return request.build_absolute_uri(path_with_query)
        return new_value


def send_email(subject, from_email, to_email, context, text_template_name, html_email_template_name=None):
    body = loader.render_to_string(text_template_name, context)
    email_message = EmailMultiAlternatives(
        subject, body, from_email, [to_email])
    if html_email_template_name is not None:
        html_email = loader.render_to_string(
            html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')
    email_message.send()


def send_email_auth_verification(user, request, subject='Authentication Verification', template_name='email/two_factor_auth.html', html_email_template_name=None,):

    # subject = loader.render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    # subject = ''.join(subject.splitlines())
    # body = loader.render_to_string(email_template_name, context)
    token = default_token_generator.make_token(user)
    to_email = user.email
    html_email_template_name = None
    context = {}
    from_email = DEFAULT_FROM_EMAIL
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    # uid_token_url = f'auth/confirm/{uid}/{token}'
    uid_token_url = reverse('email_twofactor_auth_confirm', args=[uid, token])
    current_site = get_current_site(request)
    site_name = current_site.name
    context['site_name'] = site_name
    context['password_reset_url'] = f'http://{ settings.URL_FRONT}{uid_token_url}'
    body = loader.render_to_string(template_name, context)
    email_message = EmailMultiAlternatives(
        subject, body, from_email, [to_email])
    if html_email_template_name is not None:
        html_email = loader.render_to_string(
            html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')
    email_message.send()
    return token


class CustomPasswordResetSerializer(PasswordResetSerializer):
    # def get_email_options(self):
    #     return {'domain_override': 'http://localhost:3000/',
    #             'email_template_name': 'password_reset_email.html'}
    @property
    def password_reset_form_class(self):
        # if 'allauth' in settings.INSTALLED_APPS:
        #     return AllAuthPasswordResetForm
        # else:
        return PasswordResetForm

    def save(self):
        # send the email using this new verify url
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': 'example@yourdomain.com',
            'request': request,
            'domain_override': settings.URL_FRONT,
            'token_generator': default_token_generator,
            'extra_email_context': {'URL_FRONT': settings.URL_FRONT}
            # 'email_template_name':'willpost/registration/password_reset_email.html'

        }
        opts.update(self.get_email_options())
        self.reset_form.save(**opts)


class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    def validate(self, attrs):
        from django.utils.http import urlsafe_base64_decode as uid_decoder

        # Decode the uidb64 (allauth use base36) to uid to get User object
        try:
            uid = force_str(uid_decoder(attrs['uid']))
            self.user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise ValidationError({'uid': ['Invalid value']})

        if not default_token_generator.check_token(self.user, attrs['token']):
            raise ValidationError({'token': ['Invalid value']})
        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs,
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)

        return attrs


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contact
        fields = ['id', 'email', 'phone', 'is_safe_guard',
                  'alternative_email', 'first_name', 'last_name']


class UserDetailsSerializer(serializers.ModelSerializer):
    is_expired = serializers.SerializerMethodField()
    config = serializers.SerializerMethodField()
    vote_type = serializers.ChoiceField(UserModel.VoteTypes.choices)

    def get_is_expired(self, obj):
        return obj.is_expired()

    def get_config(self, obj):
        return {'vote_type': {-1: 'NO_VOTE', 1: 'AT_LEST_ONE', 2: 'MAJORITY', 3: 'ALL'}}

    class Meta:
        model = UserModel
        fields = ['email',
                  'phone', 'vote_type', 'number_of_dayes_before_notifying', 'first_name', 'last_name', 'is_expired', 'config']
        read_only_fields = ['is_expired', 'config']

    def update(self, instance, validated_data):
        new_email = validated_data.get('email', None)
        if(new_email):
            request = self.context['request']
            try:
                email = EmailAddress.objects.get(email=instance.email)
                email.change(request, new_email)
            except EmailAddress.DoesNotExist:
                raise serializers.ValidationError(
                    "Sorry we couldn't  fillfull your request")

        return super().update(instance, validated_data)


class LoginSerializer(DefaultLoginSerializer):
    def get_auth_user(self, username, email, password):
        return self.get_auth_user_using_orm(username, email, password)

    # def validate(self, attrs):
    #     result = super().validate(attrs)
    #     user = result.get('user', None)
    #     if user:
    #         request = self.context.get('request')
    #         send_email_auth_verification(user, request)
    #     return result


class EmailTwoFactorAuthConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        from django.utils.http import urlsafe_base64_decode as uid_decoder
        try:
            uid = force_str(uid_decoder(attrs['uid']))
            self.user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise ValidationError({'uid': ['Invalid value']})

        if not default_token_generator.check_token(self.user, attrs['token']):
            raise ValidationError({'token': ['Invalid value']})

        return attrs

    def save(self):
        self.user.set_exp()


class RegisterSerializer(DefaultRegisterSerializer):
    first_name = serializers.CharField(
        required=True, max_length=150, min_length=4)
    last_name = serializers.CharField(
        required=True, max_length=150, min_length=4)

    def get_cleaned_data(self):
        super().get_cleaned_data()
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            **super().get_cleaned_data()
        }


class PostSerializer(serializers.ModelSerializer):
    # recipients = serializers.PrimaryKeyRelatedField(many=True)
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())
    file = SecuredFilePathSerializer(use_url=True)

    class Meta:
        model = models.Post
        fields = '__all__'


class PostClientSerializer(serializers.Serializer):
    urlsignature = serializers.CharField(required=True)
    post = PostSerializer(required=False)

    def validate(self, attrs):
        urlsignature = attrs.get('urlsignature')
        try:
            signature = urllib.parse.unquote_plus(urlsignature)
            post_id = signing.loads(signature, salt='Post')
            post = models.Post.objects.get(pk=post_id)
            attrs['post'] = post
        except (BadSignature, SignatureExpired, models.Post.DoesNotExist):
            raise serializers.ValidationError("Invalid Value ")
        return attrs


class VoteSerializer(serializers.Serializer):
    urlsignature = serializers.CharField(required=True)
    vote_value = serializers.ChoiceField(
        models.VoteHolder.VoteValues.choices, default=models.VoteHolder.VoteValues.UNVOTED)

    def validate(self, attrs):
        urlsignature = attrs.get('urlsignature')
        try:
            signature = urllib.parse.unquote_plus(urlsignature)
            contact_id = signing.loads(signature, salt='Contact')
            contact = models.Contact.objects.get(pk=contact_id)
            attrs['contact'] = contact
        except (BadSignature, SignatureExpired, models.Contact.DoesNotExist):
            raise serializers.ValidationError("Invalid Value ")
        return attrs

    def save(self):
        contact = self.validated_data['contact']
        vote_value = self.validated_data.get('vote_value')
        if vote_value:
            contact.vote_value = vote_value
            contact.save()


class ExistenceConfirmationSerializer(serializers.Serializer):
    urlsignature = serializers.CharField(required=True)

    def validate(self, attrs):
        urlsignature = attrs.get('urlsignature')
        try:
            signature = urllib.parse.unquote_plus(urlsignature)
            user_id = signing.loads(
                signature, max_age=timedelta(days=8), salt='User')
            user = models.User.objects.get(pk=user_id)

            attrs['user'] = user
        except (BadSignature, SignatureExpired, models.User.DoesNotExist):
            raise serializers.ValidationError("Invalid Link ")
        return attrs

    def save(self,):
        user = self.validated_data['user']
        user.set_existence_confirmation()
        user.save()

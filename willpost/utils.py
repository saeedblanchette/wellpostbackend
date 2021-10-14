from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import force_str
from django.utils.http import base36_to_int, int_to_base36, urlencode
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
##
from django.shortcuts import redirect
from django.utils.timezone import is_naive, make_aware, utc
from django.conf import settings
from calendar import month, timegm
from datetime import datetime, timedelta
from django.utils.functional import lazy
from django.core.mail import EmailMultiAlternatives
from django.template import loader


def send_email(subject, from_email, to_email, context, text_template_name, html_email_template_name=None):
    body = loader.render_to_string(text_template_name, context)
    email_message = EmailMultiAlternatives(
        subject, body, from_email, [to_email])
    if html_email_template_name is not None:
        html_email = loader.render_to_string(
            html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')
    email_message.send()


def encode_uid(pk):
    return force_str(urlsafe_base64_encode(force_bytes(pk)))


def decode_uid(pk):
    return force_str(urlsafe_base64_decode(pk))


def make_utc(dt):
    if settings.USE_TZ and is_naive(dt):
        return make_aware(dt, timezone=utc)

    return dt


def aware_utcnow():
    return make_utc(datetime.utcnow())


def datetime_to_epoch(dt):
    return timegm(dt.utctimetuple())


def datetime_from_epoch(ts):
    return make_utc(datetime.utcfromtimestamp(ts))


def format_lazy(s, *args, **kwargs):
    return s.format(*args, **kwargs)


format_lazy = lazy(format_lazy, str)


def user_pk_to_url_str(user):
    """
    This should return a string.
    """
    User = get_user_model()
    if issubclass(type(User._meta.pk), models.UUIDField):
        if isinstance(user.pk, str):
            return user.pk
        return user.pk.hex

    ret = user.pk
    if isinstance(ret, int):
        ret = int_to_base36(user.pk)
    return str(ret)


def url_str_to_user_pk(s):
    User = get_user_model()
    # TODO: Ugh, isn't there a cleaner way to determine whether or not
    # the PK is a str-like field?
    remote_field = getattr(User._meta.pk, "remote_field", None)
    if remote_field and getattr(remote_field, "to", None):
        pk_field = User._meta.pk.remote_field.to._meta.pk
    else:
        pk_field = User._meta.pk
    if issubclass(type(pk_field), models.UUIDField):
        return pk_field.to_python(s)
    try:
        pk_field.to_python("a")
        pk = s
    except ValidationError:
        pk = base36_to_int(s)
    return pk
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

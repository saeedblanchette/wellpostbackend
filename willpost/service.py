
from datetime import timedelta
from django.db.models.fields import DateTimeField
from django.utils import timezone
from willpost.serializers import send_email
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils import timezone
userModel = get_user_model()
EXISTENCE_CONFIRMATION_URL = getattr(
    settings, 'FRONEND_CONFIRMATION_URL', None)
VOTE_URL = getattr(settings, 'FRONEND_VOTE_URL', None)
if(not EXISTENCE_CONFIRMATION_URL):
    raise TypeError(
        'FRONEND_CONFIRMATION_URL attribute must defined')
SITE_NAME = getattr(
    settings, 'SITE_NAME', None)


def send_existence_confirmation():
    users = userModel.objects.filter(
        last_existence_confirmation__lte=(timezone.now()), is_active=True)
    from_email = settings.DEFAULT_FROM_EMAIL
    for user in users:
        if user.is_existence_confirmation_sent and user.existence_confirmation_grace_period_end < timezone.now():
            if user.is_sefegurad_invitation_sent and user.sefegurad_invitation_grace_period_end < timezone.now():
                # Invites contacts to read the Will
                for post in user.posts.all():
                    post.invite_recipients()
            else:
                # Invite sefe gaurds to vote
                for safe_guard in user.my_contacts.filter(is_safe_guard=True):
                    safe_guard.invite()

        else:
            # Check the user is still a life
            context = {"user": user.get_full_name(), 'site': SITE_NAME,
                       'activate_url': f'{EXISTENCE_CONFIRMATION_URL}{user.generate_existence_confirmation_signature()}'}
            send_email("User Confirmation ", from_email, user.email,
                       context, 'email/existence_confirmation.txt', 'email/existence_confirmation.html')
            user.is_existence_confirmation_sent = True
            user.save()


def tasks():
    send_existence_confirmation()

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth import get_user_model
import os
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from .utils import aware_utcnow
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
import urllib
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import signing


SITE_NAME = getattr(
    settings, 'SITE_NAME', None)
from_email = settings.DEFAULT_FROM_EMAIL


def get_frontend_post_url():
    POST_URL = getattr(settings, 'FRONEND_VOTE_URL', None)
    if(not POST_URL):
        raise TypeError(
            'FRONEND_POST_URL attribute must defined')
    return POST_URL


def get_vote_url():
    VOTE_URL = getattr(settings, 'FRONEND_VOTE_URL', None)
    if(not VOTE_URL):
        raise TypeError(
            'FRONEND_VOTE_URL attribute must defined')
    return VOTE_URL


def get_defualt_login_exp_lifetime():
    deltatime = settings.LOGIN_VERIFICATION_LIFETIME
    if not isinstance(deltatime, (timedelta)):
        raise TypeError(
            'LOGIN_VERIFICATION_LIFETIME Must be  timedelta value')
    return timezone.now()+deltatime


class TwoAuthFactorAttributesMixin(models.Model):
    exp_date_time = models.DateTimeField(
        blank=True, default=get_defualt_login_exp_lifetime)

    def set_exp(self, deltatime=None):
        " Setting expiration period for the User "
        # Todo To chack the any grammer mistakes
        if not deltatime:

            deltatime = settings.LOGIN_VERIFICATION_LIFETIME
        if not isinstance(deltatime, (timedelta)):
            raise TypeError(
                'LOGIN_VERIFICATION_LIFETIME Must be  timedelta value')
        self.exp_date_time = timezone.now()+deltatime
        self.save()

    def is_expired(self):
        " Checking the login period expiration for  the user, if it experied returns true, else false"
        return self.exp_date_time < timezone.now()

    class Meta:
        abstract = True


class VoteHolder(models.Model):
    class Meta:
        abstract = True

    class VoteValues(models.IntegerChoices):
        UNVOTED = -1
        NEUTRAL = 0
        NEGATIVE_VOTE = 1
        POSTIVE_VOTE = 2
    vote_value = models.IntegerField(
        'Vote Value', choices=VoteValues.choices, default=VoteValues.UNVOTED)


class UserVotes(models.Model):
    def get_sefegurad_invitation_grace_period_end_default():
        return timezone.now()+timedelta(days=7)

    class Meta:
        abstract = True

    class VoteTypes(models.IntegerChoices):
        NO_VOTE = -1
        AT_LEST_ONE = 1
        MAJORITY = 2
        ALL = 3
    vote_type = models.IntegerField(
        'Vote Type  ', choices=VoteTypes.choices, default=VoteTypes.NO_VOTE)
    is_sefegurad_invitation_sent = models.BooleanField(default=False)
    sefegurad_invitation_grace_period_end = models.DateTimeField(
        default=get_sefegurad_invitation_grace_period_end_default)
    # add field Voters

    def get_voteres(self):
        raise NotImplementedError(' You should implemment this method')

    @property
    def vote_results(self):
        """
        Calculate the vote result 
        """
        if self.vote_type == self.VoteTypes.NO_VOTE:
            return True
        elif self.vote_type == self.VoteTypes.AT_LEST_ONE:
            return self.vote_at_lest_one()
        elif self.vote_type == self.VoteTypes.MAJORITY:
            return self.vote_majority()
        elif self.vote_type == self.VoteTypes.ALL:
            return self.vote_all()

    def vote_all(self):
        """
        Calculate the vote resultes, 
        if all the safeguards vote ok then True, else False
        """
        votes = self.my_contacts.filter(
            is_safe_guard=True, vote_value=VoteHolder.VoteValues.POSTIVE_VOTE)
        return votes.count() == self.my_contacts.filter(is_safe_guard=True).count()

    def vote_at_lest_one(self):
        """
        Calculate the vote resultes, 
           only one postive Vote is needed for the resulting to be True
        """
        votes = self.my_contacts.filter(
            is_safe_guard=True, vote_value=VoteHolder.VoteValues.POSTIVE_VOTE).count()

        return votes > 0

    def vote_majority(self):
        """
            Calculate the vote resultes, 
            If  majority  of Vote are postive then the result is True, else False
        """
        postive_votes = self.my_contacts.filter(
            is_safe_guard=True, vote_value=VoteHolder.VoteValues.POSTIVE_VOTE).count()
        negative_votes = self.my_contacts.filter(
            is_safe_guard=True, vote_value=VoteHolder.VoteValues.NEGATIVE_VOTE).count()
        return postive_votes >= negative_votes


def get_default_last_existence_confirmation():
    return timezone.now()+timedelta(days=30)


def get_default_last_existence_confirmation_grace_period_end():
    return timezone.now()+timedelta(days=37)


class User(AbstractUser, UserVotes, TwoAuthFactorAttributesMixin):
    class UserTypes(models.IntegerChoices):
        REGISTERED = 0
        GENERATED = 1
    type = models.IntegerField(
        'User Type ', choices=UserTypes.choices, default=UserTypes.REGISTERED)
    phone = models.CharField('Phone Number', null=True, max_length=18)
    last_verifying = models.DateTimeField(default=timezone.now)
    number_of_dayes_before_notifying = models.IntegerField(
        'Number of dayes after notifyong the user', default=30)
    last_existence_confirmation = models.DateTimeField(
        default=get_default_last_existence_confirmation)
    is_existence_confirmation_sent = models.BooleanField(default=False)
    existence_confirmation_grace_period_end = models.DateTimeField(
        default=get_default_last_existence_confirmation_grace_period_end)

    # def date_to_should_notify(self):
    #     return self.last_existence_confirmation+timedelta(days=self.number_of_dayes_before_notifying) <= timezone.now()

    def generate_existence_confirmation_signature(self):
        return urllib.parse.quote_plus(signing.dumps(self.id, salt='User'))

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def set_existence_confirmation(self):
        last_existence_confirmation = timezone.now(
        )+timedelta(days=self.number_of_dayes_before_notifying)
        self.last_existence_confirmation = last_existence_confirmation
        self.existence_confirmation_grace_period_end = last_existence_confirmation + \
            timedelta(days=7)
        self.is_existence_confirmation_sent = False


class Contact(VoteHolder):
    from_user = models.ForeignKey(
        'User', related_name='my_contacts', on_delete=models.CASCADE)
    to_user = models.ForeignKey(
        'User', related_name='requests_to_contact', on_delete=models.CASCADE, null=True)
    email = models.EmailField('Email', blank=False,)
    alternative_email = models.EmailField(
        'Alternativa Email',  blank=True)
    phone = models.CharField('Phone Number', blank=True,
                             null=True, max_length=18)
    alternative_phone = models.CharField(
        'Alternativa phone Number', blank=True, null=True, max_length=18)
    first_name = models.CharField(
        'first name',  blank=False, max_length=120, null=True)
    last_name = models.CharField(
        'last name',  blank=False, max_length=120, null=True)
    is_safe_guard = models.BooleanField('Set as safeguard', default=False)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    def __str__(self):
        return self.email

    def create_associated_user(self):
        is_exists = User.objects.filter(email=self.email).exists()
        user = None
        if not is_exists:
            user = User.objects.create(username=self.username, email=self.email, first_name=self.first_name,
                                       last_name=self.last_name, type=User.UserTypes.GENERATED)
        else:
            user = User.objects.get(email=self.email)
        self.to_user = user
        return user

    def generate_vote_signature(self):
        return urllib.parse.quote_plus(signing.dumps(self.id, salt='Contact'))

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def invite(self):
        """ Invite a sefeguard to vote via email """
        from willpost.serializers import send_email
        if not self.is_safe_guard:
            raise ValueError(" You can't  Non safegaurd Contacts to Vote")
        context = {"user": self.get_full_name(), 'site': SITE_NAME,
                   'activate_url': f'{get_vote_url()}{self.generate_vote_signature()}'}
        send_email("Vote Invitation  ", from_email, self.email,
                   context, 'email/vote_invitation.txt', 'email/vote_invitation.email.html')


class Post(models.Model):
    VIDEO = 'VIDEO'
    AUDIO = 'AUDIO'
    MEDIA_TYPE = (

        (VIDEO, 'Video'),
        (AUDIO, 'Audio')
    )
    media_type = models.CharField(
        'media type', max_length=50, choices=MEDIA_TYPE, default=AUDIO)
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='posts')
    recipients = models.ManyToManyField(Contact, 'recipients')
    # video = models.FileField(null=True, blank=True)
    # # text = models.JSONField(null=True, blank=True)
    # media = models.ManyToManyField(Media, 'post', blank=True)
    file = models.FileField(null=True)

    def generate_post_signature(self):
        return urllib.parse.quote_plus(signing.dumps(self.id, salt='Post'))

    def invite_recipients(self):
        """Senting email invitaions to Will  recipients"""
        from willpost.serializers import send_email
        from_email = settings.DEFAULT_FROM_EMAIL
        for recipient in self.recipients.all():
            context = {"user": recipient.get_full_name(), 'site': SITE_NAME,
                       'activate_url': f'{get_frontend_post_url()}{self.generate_post_signature()}', 'owner': self.owner.get_full_name()}
            send_email(f" Will Invitation: Reading {self.owner.get_full_name()}  ", from_email, recipient.email,
                       context, 'email/will_invitation.txt', 'email/will_invitation.email.html')
        self.owner.is_active = False
        self.owner.save()


def _delete_file(path):
    # Deletes file from filesystem.
    if os.path.isfile(path):
        os.remove(path)


@receiver(pre_delete, sender=Post)
def delete_file_pre_delete_post(sender, instance, *args, **kwargs):
    if instance.media_type == 'Video' or instance.media_type == 'Audio':
        _delete_file(instance.file.path)

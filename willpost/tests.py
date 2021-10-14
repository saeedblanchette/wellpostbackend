from logging import fatal
from model_bakery import baker
from model_bakery.recipe import seq
from django.core import signing
from django.http import response
from django.test import TestCase, client
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from datetime import timedelta
from django.utils import timezone
from django.test import override_settings
from django.core import mail
from rest_framework.exceptions import ValidationError
from willpost.models import Contact, User, VoteHolder

from willpost.serializers import ExistenceConfirmationSerializer, VoteSerializer, send_email
from willpost.service import send_existence_confirmation
# Create your tests here.
UserModel = get_user_model()


class UserTwoFactorAuthConfirm(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            email='email@rmail.com', password='41A44qdqd5qm')
        self.user.save()
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.client = Client()
        self.client.force_login(self.user)
        self.token = default_token_generator.make_token(self.user)
        self.recipient = Contact.objects.create(
            from_user=self.user, email='email@email.com', first_name='ddqdqd', last_name='qdqdq')
        self.recipient.save()
        self.contact = baker.make('willpost.Contact')

    def test_check_exp_for_new_created_user_model(self):
        new_time = timezone.now()+timedelta(days=2)
        self.user.exp_date_time = new_time
        self.user.save()
        self.assertEqual(self.user.is_expired(), False)

    def test_check_exp_for_old_created_user_model(self):
        old_time = timezone.now()-timedelta(days=2)
        self.user.exp_date_time = old_time
        self.user.save()
        self.assertEqual(self.user.is_expired(), True)

    # def test_confirm(self):
    #     token = default_token_generator.make_token(self.user)
    #     url = reverse('email_twofactor_auth_confirm',
    #                   args=[self.uid, token])
    #     response = self.client.post(url, content_type='application/json')
    #     print( ' response ===>',response.data)
    #     self.assertEquals(response.status_code, 200)
    # @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    # def test_upload_file(self):
    #     temp_file = tempfile.NamedTemporaryFile()
    #     img = BytesIO(b'mybinarydata')
    #     img.name = 'myVide.webm'
    #     self.client = Client()
    #     self.client.force_login(self.user)
    #     with open('media/text.txt') as fp:
    #         time.sleep(5)
    #         response = self.client.post(
    #             '/media/', {'recipients': [self.recipient.id], 'file': fp})
    #     print( ' response ===>',response)
    #     self.assertEquals(response.status_code, 201)

    def test_existence_confirmation_serializer(self):
        # the successful case
        self.user.last_existence_confirmation = timezone.now()+timedelta(days=-1)
        self.user.save()
        urlsignature = self.user.generate_existence_confirmation_signature()
        serializer = ExistenceConfirmationSerializer(
            data={'urlsignature': urlsignature})
        try:
            serializer.is_valid(raise_exception=True)
            self.assertEqual(serializer.validated_data["user"], self.user)
            serializer.save()
            self.user.refresh_from_db()
            self.assertGreaterEqual(
                self.user.last_existence_confirmation, timezone.now()+timedelta(seconds=-1))
        except ValidationError:
            assert False
        # Wrong case
        urlsignature = 'hahd,ksqf*f4gfsd8g6f6'
        serializer = ExistenceConfirmationSerializer(
            data={'urlsignature': urlsignature})
        try:
            serializer.is_valid(raise_exception=True)
            self.assertEqual(serializer.validated_data["user"], self.user)
            assert False
        except ValidationError as error:
            self.assertTrue('Invalid' in str(error))
            assert True

    def test_vote_serializer_signature(self):
        # the successful case
        urlsignature = self.contact.generate_vote_signature()
        serializer = VoteSerializer(
            data={'urlsignature': urlsignature})
        try:
            serializer.is_valid(raise_exception=True)
            self.assertEqual(
                serializer.validated_data["contact"].id, self.contact.id)
            serializer.save()
            self.contact.refresh_from_db()
            self.assertEqual(self.contact.vote_value,
                             VoteHolder.VoteValues.UNVOTED)
        except ValidationError:
            assert False
        # With invalid signature
        urlsignature = "qsfdqsfqsf"
        serializer = VoteSerializer(
            data={'urlsignature': urlsignature})
        try:
            serializer.is_valid(raise_exception=True)
            self.assertEqual(
                serializer.validated_data["contact"], self.contact)
            assert False
        except ValidationError as error:
            self.assertTrue('Invalid' in str(error))
            assert True

    def test_vote_serializer_signature_and_vote_value(self):
        # with  valid case
        urlsignature = self.contact.generate_vote_signature()
        serializer = VoteSerializer(
            data={'urlsignature': urlsignature, 'vote_value': VoteHolder.VoteValues.POSTIVE_VOTE})
        try:
            serializer.is_valid(raise_exception=True)
            self.assertEqual(
                serializer.validated_data["contact"], self.contact)
            serializer.save()
            self.contact.refresh_from_db()
            self.assertEqual(self.contact.vote_value,
                             VoteHolder.VoteValues.POSTIVE_VOTE)
        except ValidationError:
            assert False
        # With invalid value
        urlsignature = self.contact.generate_vote_signature()
        serializer = VoteSerializer(
            data={'urlsignature': urlsignature, 'vote_value': 552})
        try:
            serializer.is_valid(raise_exception=True)
            assert False
        except ValidationError as error:
            self.assertTrue('invalid_choice' in str(error))
            assert True

    def test_send_email(self):
        send_email("Subject here", 'exemple@test.com', 'user12@gmail.com',
                   {"user": self.user.get_full_name, 'site': 'test'}, 'email/existence_confirmation.txt',)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(self.user.get_full_name() in mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].subject, 'Subject here')

    def test_send_existence_confirmation(self):
        baker.make('willpost.User', last_existence_confirmation=(
            timezone.now()+timedelta(days=-1)), is_active=True, _quantity=5, email=seq('user', suffix='@example.com'))
        baker.make('willpost.User', last_existence_confirmation=(timezone.now(
        )+timedelta(days=-1)), is_active=False, _quantity=3, email=seq('user', suffix='@example.com'))
        baker.make('willpost.User', last_existence_confirmation=(timezone.now(
        )+timedelta(days=1)), is_active=True, _quantity=3, email=seq('user', suffix='@example.com'))
        send_existence_confirmation()
        self.assertEqual(len(mail.outbox), 5)

    def test_send_invitaion_and_send_existence_confirmation(self):
        savegurads_set = baker.make('willpost.Contact', email=seq(
            'user', suffix='@example.com'), is_safe_guard=True, _quantity=5)
        user = baker.make('willpost.User', last_existence_confirmation=(timezone.now()+timedelta(days=-19)), is_existence_confirmation_sent=True,
                          existence_confirmation_grace_period_end=(timezone.now()+timedelta(days=-8)), is_active=True, email=seq('user', suffix='@example.com'), my_contacts=savegurads_set)

        savegurads_set = baker.make('willpost.Contact', email=seq(
            'user', suffix='@example.com'), is_safe_guard=False, _quantity=5)
        user2 = baker.make('willpost.User', last_existence_confirmation=(timezone.now()+timedelta(days=-19)), is_existence_confirmation_sent=True,
                           existence_confirmation_grace_period_end=(timezone.now()+timedelta(days=-8)), is_active=True, email=seq('user', suffix='@example.com'), my_contacts=savegurads_set)

        send_existence_confirmation()
        self.assertEqual(len(mail.outbox), 5)
    def test_safeguard_invitaion_and_send_existence_confirmation(self):
        savegurads_set = baker.make('willpost.Contact', email=seq(
            'user', suffix='@example.com'), is_safe_guard=True, _quantity=5)
        user = baker.make('willpost.User', last_existence_confirmation=(timezone.now()+timedelta(days=-19)), is_existence_confirmation_sent=True,
                          existence_confirmation_grace_period_end=(timezone.now()+timedelta(days=-8)), is_active=True, email=seq('user', suffix='@example.com'), my_contacts=savegurads_set,
                          is_sefegurad_invitation_sent=True,sefegurad_invitation_grace_period_end=(timezone.now()+timedelta(days=-2)))

        savegurads_set = baker.make('willpost.Contact', email=seq(
            'user', suffix='@example.com'), is_safe_guard=False, _quantity=5)
        user2 = baker.make('willpost.User', last_existence_confirmation=(timezone.now()+timedelta(days=-19)), is_existence_confirmation_sent=True,
                          existence_confirmation_grace_period_end=(timezone.now()+timedelta(days=-8)), is_active=True, email=seq('user', suffix='@example.com'), my_contacts=savegurads_set,
                          is_sefegurad_invitation_sent=True,sefegurad_invitation_grace_period_end=(timezone.now()+timedelta(days=+2)))

        baker.make('willpost.Post',recipients=savegurads_set,owner=user)
        baker.make('willpost.Post',recipients=savegurads_set,owner=user2)
        send_existence_confirmation()
        self.assertEqual(len(mail.outbox), 5)

    def test_vote_at_lest_one(self):
        # successefull case
        savegurads_set = baker.make('willpost.Contact', is_safe_guard=True,
                                    _quantity=1, vote_value=VoteHolder.VoteValues.POSTIVE_VOTE)
        user1 = baker.make('willpost.User', my_contacts=savegurads_set)
        self.assertEqual(user1.vote_at_lest_one(), True)
        # failed case
        savegurads_set2 = baker.make('willpost.Contact', is_safe_guard=True,
                                     _quantity=1, vote_value=VoteHolder.VoteValues.NEGATIVE_VOTE)
        user2 = baker.make('willpost.User', my_contacts=savegurads_set2)

        self.assertEqual(user2.vote_at_lest_one(), False)

    def test_vote_all(self):
        # successefull case
        # all save guards vote with Yes
        savegurads_set = baker.make('willpost.Contact', is_safe_guard=True,
                                    _quantity=3, vote_value=VoteHolder.VoteValues.POSTIVE_VOTE)
        user1 = baker.make('willpost.User', my_contacts=savegurads_set)
        self.assertEqual(user1.vote_all(), True)

        # failed case
        savegurads_set2 = baker.make('willpost.Contact', is_safe_guard=True,
                                     _quantity=3, vote_value=VoteHolder.VoteValues.NEGATIVE_VOTE)
        user2 = baker.make('willpost.User', my_contacts=savegurads_set2)
        self.assertEqual(user2.vote_all(), False)
        # one save guards vote with No amoung othe who vote yes
        savegurad_with_no = baker.make('willpost.Contact', is_safe_guard=True,
                                       _quantity=1, vote_value=VoteHolder.VoteValues.NEGATIVE_VOTE)
        savegurads_set.append(savegurad_with_no[0])
        user3 = baker.make('willpost.User', my_contacts=savegurads_set)
        self.assertEqual(user3.vote_all(), False)

    def test_vote_majority(self):
        # successefull case
        # all save guards vote with Yes
        savegurads_set = baker.make('willpost.Contact', is_safe_guard=True,
                                    _quantity=3, vote_value=VoteHolder.VoteValues.POSTIVE_VOTE)
        user1 = baker.make('willpost.User', my_contacts=savegurads_set)
        self.assertEqual(user1.vote_majority(), True)
        savegurads_set_negative = baker.make('willpost.Contact', is_safe_guard=True,
                                             _quantity=2, vote_value=VoteHolder.VoteValues.NEGATIVE_VOTE)
        savegurads_set.extend(savegurads_set_negative)
        user2 = baker.make('willpost.User', my_contacts=savegurads_set)
        self.assertEqual(user2.vote_majority(), True)
        # failed case
        savegurads_set3 = baker.make('willpost.Contact', is_safe_guard=True,
                                     _quantity=4, vote_value=VoteHolder.VoteValues.NEGATIVE_VOTE)
        user3 = baker.make('willpost.User', my_contacts=savegurads_set3)
        self.assertEqual(user3.vote_all(), False)
        savegurads_set3.extend(savegurads_set)
        user3 = baker.make('willpost.User', my_contacts=savegurads_set)
        self.assertEqual(user3.vote_all(), False)

    def test_invite_recipiets(self):
        recipients_set = baker.make('willpost.Contact', _quantity=3)
        post = baker.make('willpost.Post', recipients=recipients_set)
        post.invite_recipients()
        self.assertEqual(len(mail.outbox), 3)

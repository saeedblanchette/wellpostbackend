from rest_framework import response
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import generics
from willpost import serializers, models
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from willpost.permissions import TwoAuthFactorPermission
from dj_rest_auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.db import transaction


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    # OnlyTheAssociatContact
    permission_classes = [IsAuthenticated, TwoAuthFactorPermission]
    serializer_class = serializers.ContactSerializer

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        user=self.request.user
        return models.Contact.objects.filter(from_user=user)


class ContactListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, TwoAuthFactorPermission]
    serializer_class = serializers.ContactSerializer

    def get_queryset(self):
        user=self.request.user
        return models.Contact.objects.filter(from_user=user)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)


class UserDetailsView(generics.RetrieveUpdateAPIView):
    """
    Reads and updates UserModel fields
    Accepts GET, PUT, PATCH methods.
    Default accepted fields: username, first_name, last_name
    Default display fields: pk, username, email, first_name, last_name
    Read-only fields: pk, email
    Returns UserModel fields.
    """
    serializer_class = serializers.UserDetailsSerializer
    permission_classes = (IsAuthenticated, TwoAuthFactorPermission)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        newemail = serializer.validated_data.get('email', None)
        if(newemail):
            return Response({'email': 'activation link  has been sent e-mail'}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.data)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        """
        Adding this method since it is sometimes called when using
        django-rest-swagger
        """
        return get_user_model().objects.none()


class EmailTwoFactorAuthConfirm(APIView):
    serializer_class = serializers.EmailTwoFactorAuthConfirmSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, uid, token):
        serializer = self.serializer_class(data={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": 'login successed '}, status=status.HTTP_200_OK)


TwoFactorAuthConfirm = EmailTwoFactorAuthConfirm.as_view()


class EmailTwoFactorAuthSendView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializers.send_email_auth_verification(request.user, request)
        return Response({"detail": 'verification successed '}, status=status.HTTP_200_OK)


class CLoginView(LoginView):
    permission_classes = (AllowAny,)

    def post(self, request):
        response = super().post(request)
        if request.user.is_expired():
            serializers.send_email_auth_verification(request.user, request)
        return response


class MediaListView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = serializers.PostSerializer

    def get_queryset(self):
        return models.Post.objects.filter(owner=self.request.user)

    def get(self, request):
        queryset = self.get_queryset()
        context = {'request': request}
        serializer = self.serializer_class(
            queryset, many=True, context=context)
        return Response(data=serializer.data, status=200)

    def post(self, request, format=None):
        with transaction.atomic():
            serializer = self.serializer_class(
                data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            print(' File', serializer.validated_data['file'])
            serializer.save(owner=request.user)

        return Response(data=serializer.data, status=201)


class MediaDetailView(APIView):
    parser_classes = [MultiPartParser]
    serializer_class = serializers.PostSerializer
    permission_classes = [IsAuthenticated]

    # def get_object(self):
    #     obj = get_object_or_404(models.Post, pk=pk)
    #     self.check_object_permissions(self.request, obj)
    #     return obj

    def get(self, request, pk, format=None):
        obj = get_object_or_404(models.Post, pk=pk)
        self.check_object_permissions(self.request, obj)
        self.serializer_class(data=obj)
        return Response(data=obj, status=200)

    def put(self, request, pk, format=None):
        obj = get_object_or_404(models.Post, pk=pk)
        self.check_object_permissions(self.request, obj)
        serializer = self.serializer_class(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=200)

    def patch(self, request, pk, format=None):
        obj = get_object_or_404(models.Post, pk=pk)
        self.check_object_permissions(self.request, obj)
        serializer = self.serializer_class(
            instance=obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=200)

    def delete(self, request, pk, format=None):
        obj = get_object_or_404(models.Post, pk=pk)
        self.check_object_permissions(self.request, obj)
        obj.delete()
        return Response(status=204)


class ExistenceConfirmationView(APIView):
    serializer_class = serializers.ExistenceConfirmationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serialzer = self.serializer_class(data=request.data)
        serialzer.is_valid(raise_exception=True)
        serialzer.save()
        return Response(status=status.HTTP_200_OK)

    # def post(self, request):
    #     serialzer = self.serializer_class(data=request.data)
    #     serialzer.is_valid()
    #     serialzer.save()
    #     Response(status=status.HTTP_200_OK)


class VoteView(APIView):
    serializer_class = serializers.VoteSerializer
    permission_classes = [AllowAny]

    def get(self, request, urlsignature):
        serialzer = self.serializer_class(data={'urlsignature': urlsignature})
        serialzer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        serialzer = self.serializer_class(data=request.data)
        serialzer.is_valid()
        serialzer.save()
        return Response(status=status.HTTP_200_OK)


class PostView(APIView):
    serializer_class = serializers.PostClientSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def get(self, request, urlsignature):
        serialzer = self.serializer_class(data={'urlsignature': urlsignature},context={'request':request})
        serialzer.is_valid(raise_exception=True)
        post = models.Post.objects.get(pk=serialzer.data['post']['id'])
        post_ser = serializers.PostSerializer(post,context={'request':request})
        return Response(data=serialzer.data['post'], status=status.HTTP_200_OK)


class ServeMedia(APIView):
    serializer_class = serializers.PostClientSerializer
    permission_classes = [AllowAny]

    def get(self, request,file ):

        response = Response()
        response['X-Accel-Redirect'] = '/protected'+request.path
        return response
       

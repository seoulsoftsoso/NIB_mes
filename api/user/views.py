import traceback
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.db import transaction
from api.models import UserMaster, Menu_Auth
from api.serializers import UserMasterSerializer
from rest_framework import status
from msgs import *


# from api.user.authentication import get_expire_time


class CustomObtainAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        #         Token.objects.filter(user=user, created__lt=get_expire_time()).delete()

        token, created = Token.objects.get_or_create(user=user)

        #로그인 정보 세션 저장
        login(request, user)

        return Response({'token': token.key, 'user': UserMasterSerializer(user).data}, status=status.HTTP_200_OK)


class UserCreate(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            formData = request.POST
            password = formData.get('user_pwd')
            clean_password = make_password(password)

            usermaster = UserMaster.objects.create(
                password=clean_password,
                last_login=timezone.now(),
                is_superuser=False,
                user_id=formData.get("add_user_id"),
                username=formData.get("add_username"),
                is_master=False,
                auth='Admin'
            )

            Menu_Auth.objects.create(
                alias='설정',
                order=1000,
                menu_id=125,
                created_by_id=usermaster.id,
                updated_by_id=usermaster.id,
                user_id=usermaster.id,
            )

            Menu_Auth.objects.create(
                alias='회사 설정',
                order=1010,
                menu_id=126,
                parent_id=125,
                created_by_id=usermaster.id,
                updated_by_id=usermaster.id,
                user_id=usermaster.id,
            )

            Menu_Auth.objects.create(
                alias='멤버 설정',
                order=1020,
                menu_id=106,
                parent_id=125,
                created_by_id=usermaster.id,
                updated_by_id=usermaster.id,
                user_id=usermaster.id,
            )

            Menu_Auth.objects.create(
                alias='메뉴 설정',
                order=1030,
                menu_id=111,
                parent_id=125,
                created_by_id=usermaster.id,
                updated_by_id=usermaster.id,
                user_id=usermaster.id,
            )

            return JsonResponse({'success': True, 'message': msg_cre_ok})

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)

import traceback

from django.db import IntegrityError
from django.forms import model_to_dict
from django.utils import timezone

from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views import View

from api.models import UserMaster, CodeMaster
from msgs import *


def get_departments_object(request):
    qs = CodeMaster.objects.filter(enterprise_id=request.user.enterprise_id, group_id=2).values('id', 'code', 'name')
    result = list(qs)
    return result


def get_job_position_object(request):
    qs = CodeMaster.objects.filter(enterprise_id=request.user.enterprise_id, group_id=1).values('id', 'code', 'name')
    result = list(qs)
    return result


class GetDepartments(View):
    def get(self, request):
        result = get_departments_object(request)
        return JsonResponse({'result': result})


class GetJobPositions(View):
    def get(self, request):
        result = get_job_position_object(request)
        return JsonResponse({'result': result})


class MemberCreate(View):
    def post(self, request, *args, **kwargs):
        try:
            formdata = request.POST

            password = formdata.get('user_pwd')
            clean_password = make_password(password)

            UserMaster.objects.create(
                last_login=timezone.now(),
                is_superuser=False,
                is_master=False,
                username=formdata.get('add_username'),
                user_id=formdata.get('add_user_id'),
                password=clean_password,
                employment_date=formdata.get('employment_date'),
                department_position_id=formdata.get('add_department_position'),
                job_position_id=formdata.get('add_job_position'),
                enterprise_id=request.user.enterprise_id,
                email=formdata.get('add_email'),
                tel=formdata.get('add_tel'),
                etc=formdata.get('add_memo'),
            )

            return JsonResponse({'success': True, 'message': msg_cre_ok})

        except IntegrityError as e:
            if 'user_id' in str(e):
                return JsonResponse({'error': '중복된 아이디입니다.'}, status=400)

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


class MemberUpdate(View):
    def post(self, request, *args, **kwargs):
        try:
            formdata = request.POST
            type = request.POST.get('type')
            usermaster = UserMaster.objects.get(id=formdata.get('user_id'))
            if type == "E":
                usermaster.username = formdata.get('username')
                usermaster.department_position_id = formdata.get('department_position')
                usermaster.auth = formdata.get('auth')
                usermaster.email = formdata.get('email')
                usermaster.tel = formdata.get('tel')
                usermaster.etc = formdata.get('memo')
                usermaster.save()

                return JsonResponse({'success': True, 'message': msg_edit_ok})

            elif type == "D":

                usermaster.del_flag = 'Y'
                usermaster.save()

                return JsonResponse({'success': True, 'message': msg_del_ok})

            else:
                return JsonResponse({'error': 'Invalid type provided.'}, status=400)

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


class GetMembers(View):
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.GET.get('user_id')

            usermaster = UserMaster.objects.get(id=user_id)
            result = model_to_dict(usermaster)

            return JsonResponse({'result': result})

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)

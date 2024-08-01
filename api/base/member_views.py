import traceback
from django.http import JsonResponse
from django.views import View

from api.models import UserMaster, CodeMaster
from msgs import *


def get_departments_object():
    qs = CodeMaster.objects.filter(group_id=2).values('id', 'code', 'name')
    result = list(qs)
    return result


class GetDepartments(View):
    def get(self, request):
        result = get_departments_object()
        return JsonResponse({'result': result})


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

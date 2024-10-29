import traceback
from django.http import JsonResponse
from django.views import View

from api.models import RobotMaster
from msgs import *


class CreateRobot(View):

    def post(self, request, *args, **kwargs):
        try:
            formdata = request.POST

            RobotMaster.objects.create(
                name=formdata.get('name'),
                code=formdata.get('code'),
                model=formdata.get('model'),
                make_co=formdata.get('make_co'),
                work_loc_id=formdata.get('work_loc'),
                memo=formdata.get('memo'),
                created_by_id=request.user.id,
                enterprise_id=request.user.enterprise_id,
            )

            return JsonResponse({'success': True, 'message': msg_cre_ok})

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


class UpdateRobot(View):
    def post(self, request, *args, **kwargs):
        try:
            type = request.POST.get('type')
            formdata = request.POST
            robot = RobotMaster.objects.get(id=formdata.get('robot_id'))
            if type == 'E':

                robot.name = formdata.get('edit_name')
                robot.code = formdata.get('edit_code')
                robot.model = formdata.get('edit_model')
                robot.make_co = formdata.get('edit_make_co')
                robot.work_loc_id = formdata.get('edit_work_loc')
                robot.memo = formdata.get('edit_memo')
                robot.save()

                return JsonResponse({'success': True, 'message': msg_cre_ok})

            elif type == 'D':

                robot.del_flag = 'Y'
                robot.save()
                # 나중에 히스토리 모델에도 del_flag = 'Y'로 수정해야 됨.

                return JsonResponse({'success': True, 'message': msg_del_ok})

            return JsonResponse({'error': True}, status=400)

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)

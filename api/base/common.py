import traceback

from django.db.models import Q
from django.views import View
from django.http import JsonResponse
from api.models import CustomerMaster, Warehouse
from msgs import *


class WishUpdate(View):
    def get(self, request, *args, **kwargs):
        print(request.GET)
        model_type = request.GET.get('model')
        try:
            if model_type == 'CustomerMaster':
                customer = CustomerMaster.objects.get(id=request.GET.get('id'))
                customer.wish_flag = not customer.wish_flag
                customer.save()

                return JsonResponse({'success': True, 'message': msg_edit_ok})

            elif model_type == 'Warehouse':
                warehouse = Warehouse.objects.get(id=request.GET.get('id'))
                warehouse.wish_flag = not warehouse.wish_flag
                warehouse.save()

                return JsonResponse({'success': True, 'message': msg_edit_ok})

            else:
                return JsonResponse({'error': 'Invalid type provided.'}, status=400)

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)

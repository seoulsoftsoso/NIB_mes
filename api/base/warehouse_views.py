import traceback

from django.db.models import Q
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import CustomerMaster, Warehouse, WarehouseRack, ItemIn, ItemOut, StockStatus
from msgs import *

"""
창고 views
"""


def get_warehouse_master(enterprise, search_term=''):
    qs = Warehouse.objects.filter(enterprise=enterprise, del_flag="N")

    if search_term:
        qs = qs.filter(
            Q(name__icontains=search_term) |
            Q(code__icontains=search_term) |
            Q(region__icontains=search_term)
        )

    qs = qs.values('id', 'code', 'name', 'region', 'created_by_id', 'enterprise_id')
    result = list(qs)
    return result


class GetWarehouse(View):
    def get(self, request, *args, **kwargs):
        enterprise = request.user.enterprise_id
        search_term = request.GET.get('search', '')
        warehouse = get_warehouse_master(enterprise=enterprise, search_term=search_term)
        context = {'result': warehouse}
        return JsonResponse(context)


class WarehouseCreate(View):
    def post(self, request, *args, **kwargs):
        formdata = request.POST
        enterprise = request.user.enterprise_id

        try:
            warehouse = Warehouse(
                name=formdata.get('name'),
                region=formdata.get('region'),
                enterprise_id=enterprise,
                created_by_id=request.user.id,
            )

            warehouse.save()

            rack = warehouse.warehouse_rack.create(
                rack_name=formdata.get('rack_name'),
                rack_row=formdata.get('row'),
                rack_line=formdata.get('col'),
                wr_etc=formdata.get('memo'),
                created_by_id=request.user.id,
            )

            rack.save()

            return JsonResponse({
                'success': True,
                'message': msg_cre_ok,
                'id': warehouse.id,
                'name': warehouse.name
            })

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


class WarehouseUpdate(View):
    def post(self, request, *args, **kwargs):
        type = request.POST.get('type')
        try:
            if type == 'E':
                print('?????????????????????????')
                formdata = request.POST

                wh = Warehouse.objects.get(id=formdata.get('wh_id'))
                wh.name = formdata.get('edit_name')
                wh.region = formdata.get('edit_region')
                wh.save()

                wr = WarehouseRack.objects.get(warehouse_id=formdata.get('wh_id'))
                wr.rack_name = formdata.get('edit_rack_name')
                wr.rack_row = formdata.get('edit_row')
                wr.rack_line = formdata.get('edit_col')
                wr.wr_etc = formdata.get('edit_memo')
                wr.save()

                return JsonResponse({'success': True, 'message': msg_edit_ok})

            elif type == 'D':
                formdata = request.POST
                wh = Warehouse.objects.get(id=formdata.get('wh_id'))
                wh.del_flag = "Y"
                wh.save()

                WarehouseRack.objects.filter(warehouse=wh).update(del_flag="Y")
                ItemIn.objects.filter(wh=wh).update(del_flag="Y")
                ItemOut.objects.filter(out_wh=wh).update(del_flag="Y")
                StockStatus.objects.filter(wh=wh).update(del_flag="Y")

                return JsonResponse({'success': True, 'message': msg_del_ok})

            else:
                return JsonResponse({'error': 'Invalid type provided.'}, status=400)

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)

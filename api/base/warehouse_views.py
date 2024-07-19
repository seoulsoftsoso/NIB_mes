import traceback

from django.db.models import Q
from django.views import View
from django.http import JsonResponse
from api.models import CustomerMaster, Warehouse

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

            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)

import traceback

from django.db.models import Q
from django.views import View
from django.http import JsonResponse
from api.models import CustomerMaster
from msgs import *


def get_customer_master(enterprise, search_term=''):
    query = CustomerMaster.objects.filter(enterprise=enterprise, del_flag='N')

    if search_term:
        query = query.filter(
            Q(c_name__icontains=search_term) |
            Q(business_num__icontains=search_term) |
            Q(owner_name__icontains=search_term)
        )

    query = query.values(
        'id', 'c_name', 'business_num', 'business_type', 'business_sort', 'postal_code', 'address', 'sign', 'logo',
        'owner_name', 'official_tel', 'official_fax', 'official_email', 'manager_tel', 'manager_email', 'memo',
        'created_by_id', 'enterprise_id'
    )

    result = list(query)
    return result


class GetCustomer(View):
    def get(self, request, *args, **kwargs):
        enterprise = request.user.enterprise_id
        search_term = request.GET.get('search', '')
        customer = get_customer_master(enterprise=enterprise, search_term=search_term)
        context = {'result': customer}
        return JsonResponse(context)


class CustomerCreate(View):
    def post(self, request, *args, **kwargs):
        try:
            formdata = request.POST
            print('formdata', formdata)
            customer = CustomerMaster(
                c_name=formdata.get('c_name'),
                business_num=formdata.get('business_num'),
                business_type=formdata.get('business_type'),
                business_sort=formdata.get('business_sort'),
                address=formdata.get('address'),
                owner_name=formdata.get('owner_name'),
                official_tel=formdata.get('official_tel'),
                official_email=formdata.get('official_email'),
                manager_tel=formdata.get('manager_tel'),
                manager_email=formdata.get('manager_email'),
                memo=formdata.get('memo'),
                enterprise_id=request.user.enterprise_id,
                created_by_id=request.user.id
            )

            customer.save()

            return JsonResponse({
                'success': True,
                'message': msg_cre_ok,
                'id': customer.id,
                'name': customer.c_name
            })

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


class CustomerUpdate(View):
    def post(self, request, *args, **kwargs):
        type = request.POST.get('type')
        formdata = request.POST
        customer = CustomerMaster.objects.get(id=formdata.get('c_id'))
        try:
            if type == "E":

                customer.c_name = formdata.get('c_name')
                customer.business_num = formdata.get('business_num')
                customer.business_type = formdata.get('business_type')
                customer.business_sort = formdata.get('business_sort')
                customer.address = formdata.get('address')
                customer.owner_name = formdata.get('owner_name')
                customer.official_tel = formdata.get('official_tel')
                customer.official_email = formdata.get('official_email')
                customer.manager_tel = formdata.get('manager_tel')
                customer.manager_email = formdata.get('manager_email')
                customer.save()

                return JsonResponse({'success': True, 'message': msg_edit_ok})

            elif type == "D":

                customer.del_flag = "Y"
                customer.save()

                return JsonResponse({'success': True, 'message': msg_del_ok})

            else:
                return JsonResponse({'error': 'Invalid type provided.'}, status=400)

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)

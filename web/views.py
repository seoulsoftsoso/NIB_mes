from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect

from api.Delivery.delivery_api import *
from api.Item.common import get_item_data
from api.base.base_form import enterprise_fm
from api.models import MenuMaster, ItemMaster, UnitPrice, ItemIn, Warehouse, ItemOut, CustomerMaster, UserMaster
from dve_config import settings


@login_required
def index(request):
    if request.user.enterprise_id == 100:
        return redirect('/sign-up/add_info')

    return render(request, 'index.html', {})


def login_page(request):
    return render(request, 'login.html', {})


def sign_up_page(request):
    return render(request, 'sign-up.html', {})


def sign_up_add_info_page(request):
    return render(request, 'sign-up-add-info.html', {})


def register_page(request):
    return render(request, 'register.html', {})


def register_ok(request):
    return render(request, 'register_ok.html', {})


def codemaster(request):
    context = {}
    return render(request, 'basic_information/codemaster.html', context)


def new_enterprise(request):
    context = {}

    # column = getColumnList(request.COOKIES['enterprise_id'], request.COOKIES['user_id'], 109, 'M')
    # context['column'] = column

    return render(request, 'basic_information/new_enterprise_register.html', context)


def Menumaster(request):
    context = {}
    enter = enterprise_fm(request.GET, request.user.enterprise.name)
    # enter = enterprise_fm(request.GET, request.COOKIES['enterprise_name'])
    context['ep'] = enter
    return render(request, 'Setting/Menu/menumaster.html', context)


def UserBasedInfo(request):
    enterprise = request.user.enterprise_id

    qs = UserMaster.objects.filter(enterprise_id=enterprise, del_flag="N", is_superuser=False)

    context = {
        'result': qs
    }
    return render(request, 'Setting/Member/main.html', context)


def DeptMgmt(request):
    context = {}
    return render(request, 'basic_information/dept_mgmt.html', context)


def customer_info(request):
    enterprise = request.user.enterprise_id

    qs = CustomerMaster.objects.filter(del_flag='N', enterprise_id=enterprise).values(
        'id', 'c_name', 'business_num', 'business_type', 'business_sort', 'postal_code', 'address', 'owner_name',
        'official_tel', 'official_fax', 'official_email', 'manager_tel', 'manager_email', 'memo', 'wish_flag'
    ).order_by('-wish_flag', '-id')

    context = {
        'result': qs
    }
    return render(request, 'basic_information/Customer/main.html', context)


def Material_input(request):
    enterprise = request.user.enterprise_id
    item_in = ItemIn.objects.filter(
        created_by__enterprise_id=enterprise,
        del_flag='N'
    ).select_related('in_custom', 'in_item', 'uprice', 'wh', 'wr').order_by('-id')

    # 필터용
    wh_filter = Warehouse.objects.filter(created_by__enterprise_id=enterprise, del_flag='N')

    context = {
        'result': item_in,
        'wh_filter': wh_filter,
        'item_in_filter': ItemIn.IN_STATUS_CHOICES,
        'item_type_choices': ItemMaster.ITEM_TYPE_CHOICES
    }
    return render(request, 'Material/init_mgmt/material_input.html', context)


def Material_output(request):
    enterprise = request.user.enterprise_id
    item_out = ItemOut.objects.filter(
        created_by__enterprise_id=enterprise,
        del_flag='N'
    ).select_related('out_custom', 'out_item', 'out_uprice', 'out_wh', 'out_wr').order_by('-id')

    # 필터용
    wh_filter = Warehouse.objects.filter(created_by__enterprise_id=enterprise, del_flag='N')

    context = {
        'result': item_out,
        'wh_filter': wh_filter,
        'item_out_filter': ItemIn.IN_STATUS_CHOICES,
        'item_type_choices': ItemMaster.ITEM_TYPE_CHOICES
    }
    return render(request, 'Material/out_mgmt/material_output.html', context)


def dashboard_page(request):
    context = {}
    return render(request, 'dashboard.html', context)


def Material_status(request):
    enterprise = request.user.enterprise_id

    items = get_item_data(enterprise_id=enterprise)
    context = {
        'result': items,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'Material/material_list/main.html', context)


def item_info(request):
    enterprise = request.user.enterprise_id

    result = ItemMaster.objects.filter(del_flag='N', enterprise_id=enterprise).prefetch_related(
        Prefetch('unit_prise_item', queryset=UnitPrice.objects.filter(del_flag='N'))
    )

    context = {
        'result': result,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    return render(request, 'basic_information/Item/item_info.html', context)


def Material_Adjustment(request):

    context = {}
    return render(request, 'Material/adjustment/main.html', context)


def warehouse_info(request):
    enterprise = request.user.enterprise_id
    result = Warehouse.objects.filter(del_flag='N', enterprise_id=enterprise).annotate(
        total_quantity=Coalesce(Sum('stock_warehouse__quantity'), 0)
    ).values(
        'id', 'code', 'name', 'region', 'enterprise', 'del_flag', 'updated_at', 'created_by', 'total_quantity',
        'warehouse_rack__rack_name', 'warehouse_rack__rack_row', 'warehouse_rack__rack_line', 'warehouse_rack__wr_etc',
        'wish_flag'
    ).order_by('-wish_flag', '-id')

    context = {
        'result': result
    }
    return render(request, 'basic_information/Warehouse/main.html', context)


def error_page(request):
    context = {}
    return render(request, 'error_404.html', context)


def delivery_page(request):
    result = DeliveryList()
    DeliveryTrack()
    context = {
        'result': result
    }
    return render(request, 'Delivery/main.html', context)


def test_page(request):
    context = {}
    return render(request, 'Delivery/test.html', context)


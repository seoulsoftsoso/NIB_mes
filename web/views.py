from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render

from api.Item.common import get_item_data
from api.base.base_form import enterprise_fm
from api.models import MenuMaster, ItemMaster, UnitPrice, ItemIn, Warehouse, ItemOut
from dve_config import settings


@login_required
def index(request):
    return render(request, 'index.html', {})


def login_page(request):
    return render(request, 'login.html', {})


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
    # allMenu = MenuMaster.objects.filter(type='L').order_by('id')
    # useMenu = MenuMaster.objects.filter(menuauth__enterprise=request.COOKIES.get("enterprise_id")
    #                                     , menuauth__user=request.COOKIES.get('user_id')
    #                                     , menuauth__use_flag='Y'
    #                                     , menuauth__del_flag='N'
    #                                     , menuauth__parent_id=0
    #                                     ).annotate(alias=Coalesce('menuauth__alias', F('name'))
    #                                                ).values('id', 'code', 'alias', 'path', 'type', 'comment', 'i_class'
    #                                                         , 'created_by_id', 'created_at', 'updated_by_id',
    #                                                         'updated_at'
    #                                                         , 'del_flag').order_by('menuauth__order')
    #
    enter = enterprise_fm(request.GET, request.COOKIES['enterprise_name'])
    # context['allMenu'] = allMenu
    # context['useMenu'] = useMenu
    context['ep'] = enter
    return render(request, 'basic_information/menumaster.html', context)


def UserBasedInfo(request):
    context = {}
    return render(request, 'basic_information/user_based_info.html', context)


def DeptMgmt(request):
    context = {}
    return render(request, 'basic_information/dept_mgmt.html', context)


def CompanyMgmt(request):
    context = {}
    return render(request, 'basic_information/company_mgmt.html', context)


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
        'warehouse_rack__rack_name', 'warehouse_rack__rack_row', 'warehouse_rack__rack_line', 'warehouse_rack__wr_etc'
    )

    context = {
        'result': result
    }
    return render(request, 'basic_information/Warehouse/main.html', context)



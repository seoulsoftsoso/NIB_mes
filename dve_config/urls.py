"""dve_mes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from django.views.static import serve
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from api.Item.common import *
from api.Item.item_adjustment import *
from api.Item.item_input import *
from api.Item.item_output import *
from api.auto_complete import enterprise_name_ac, client_name_ac
from api.base.codemaster_views import CodeMasterViewSet, CodeMasterSelectView
from api.base.customer_views import *

from api.base.enterprise_views import EnterpriseMasterViewSet, EnterpriseCreate

from api.base.groupcodemaster_views import GroupCodeMasterViewSet, GenerateCodeMaster
from api.base.member_views import *
from api.base.warehouse_views import *
from api.base.common import *
from api.base.menu_config import MenuHandler, getLmenuList, setMenuByUser

from api.base.user_views import UserMasterViewSet, UserMasterSelectViewSet

from api.user.views import CustomObtainAuthToken, UserCreate, check_duplicate_id

from web.views import *

from django.conf import settings
from django.conf.urls.static import static

TITLE = "서울소프트 통합 MES를 위한 프로젝트 API"
VERSION = "v0.1"
DESCRIPTION = """
 # 1차개발 목표 : WMS
 # 2차개발 목표 : MES
 # 3차개발 목표 : ERP
"""

# drf yasg
schema_view = get_schema_view(
    openapi.Info(
        title=TITLE,
        default_version=VERSION,
        description=DESCRIPTION,
        # terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="grammaright@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

#########################
# define router
#########################
router = DefaultRouter()

# 기준정보
router.register(r'enterprises', EnterpriseMasterViewSet)
router.register(r'group_codes', GroupCodeMasterViewSet)
router.register(r'generate_codes', GenerateCodeMaster)
router.register(r'codes', CodeMasterViewSet)
router.register(r'codes_select', CodeMasterSelectView)

router.register(r'users', UserMasterViewSet)
router.register(r'users_select', UserMasterSelectViewSet)

router.register(r'getMenulist', MenuHandler)  #업체,사용자별 메뉴 조회

custom_obtain_auth_token = CustomObtainAuthToken.as_view()

urlpatterns = [

                path('', index),
                path('accounts/login/', login_page),
                path('login/', login_page),
                path('logout/', auth_views.LogoutView.as_view(), name='logout'),
                path('sign-up/', sign_up_page, name='sign_up_page'),
                path('sign-up/add_info', sign_up_add_info_page, name='sign_up_add_info_page'),
                path('user-create/', UserCreate.as_view(), name='UserCreate'),
                path('check_duplicat_id/', check_duplicate_id, name='check_duplicate_id'),
                path('users/login/', custom_obtain_auth_token),
                re_path(r'^data/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),

                path('dashboard/', dashboard_page, name="dashboard_page"),

                # 설정
                path('settings/menumaster/', Menumaster, name="MenuMaster"),
                path('settings/member/', UserBasedInfo, name='UserBasedInfo'),
                path('enterprise_create/', EnterpriseCreate.as_view(), name='EnterpriseCreate'),

                # 기준 정보
                path('basic_information/codemaster/', codemaster),
                path('basic_information/enterprise/', new_enterprise),
                path('basic_information/getlmenulist/', getLmenuList),
                path('basic_information/setmenubyuser/', setMenuByUser.as_view(), name='setmenubyuser'),
                #path('getMenulist/', MenuHandler)
                path('basic_information/dept_mgmt/', DeptMgmt, name='DeptMgmt'),
                path('basic_information/customer/', customer_info, name='customer_info'),
                path('basic_information/item/', item_info, name='item_info'),
                path('basic_information/wh_info/', warehouse_info, name='warehouse_info'),
                # 멤버
                path('member/create/', MemberCreate.as_view(), name='MemberCreate'),
                path('member/update/', MemberUpdate.as_view(), name='MemberUpdate'),
                path('get_department', GetDepartments.as_view(), name='GetDepartments'),
                path('get_job_position', GetJobPositions.as_view(), name='GetJobPositions'),

                # 거래처
                path('customer/get', GetCustomer.as_view(), name='GetCustomer'),
                path('customer/create', CustomerCreate.as_view(), name='CustomerCreate'),
                path('customer/update', CustomerUpdate.as_view(), name='CustomerUpdate'),

                # 즐겨찾기
                path('wish/update', WishUpdate.as_view(), name='WishUpdate'),

                # 창고
                path('warehouse/get', GetWarehouse.as_view(), name='GetWarehouse'),
                path('warehouse/create', WarehouseCreate.as_view(), name='WarehouseCreate'),
                path('warehouse/update', WarehouseUpdate.as_view(), name='WarehouseUpdate'),

                # 재고 관리 페이지
                path('material/status/', Material_status, name='Material_status'),  # 재고 목록
                path('material/input/', Material_input, name='Material_input'),  # 입고
                path('material/output/', Material_output, name='Material_output'),  # 출고

                # 재고 입고
                path('material/input/get', InputGet.as_view(), name='InputGet'),
                path('material/input/create', InputCreate.as_view(), name='InputCreate'),
                path('material/input/update', InputUpdate.as_view(), name='InputUpdate'),
                path('material/input/filtering', ItemInFilter.as_view(), name='ItemInFilter'),

                # 재고 출고
                path('material/output/get', OutputGet.as_view(), name='OutputGet'),
                path('material/output/create', OutputCreate.as_view(), name='OutputCreate'),
                path('material/output/update', OutputUpdate.as_view(), name='OutputUpdate'),
                path('material/output/filtering', ItemOutFilter.as_view(), name='ItemOutFilter'),

                # 재고 조정
                path('material/get_material/', get_material_data, name='get_material_data'),
                path('material/adjust/', Material_Adjustment, name='Material_Adjustment'),
                path('material/adjust/count', AdjustCount.as_view(), name='AdjustCount'),
                path('material/adjust/location', AdjustLocation.as_view(), name='AdjustLocation'),


                # 재고 현황
                path('material/stock_get/', GetStock.as_view(), name='GetStock'),

                # Item
                path('item/get/', get_item_masters.as_view(), name='get_item_masters'),  # 품목 전체
                path('item/get/one', get_one_item_masters.as_view(), name='get_one_item_masters'),  # 품목 한개
                path('item/add/', ItemAdd.as_view(), name='ItemAdd'),  # 품목 추가
                path('item/update/', Update_Item.as_view(), name='update_item'),

                # 출하 관리
                path('ordering_ex/ordering_export_status/', delivery_page, name='delivery_page'),

                # QRCode_In
                path('qr_code/item_detail/<int:item_id>/', qr_in_item_detail, name='qr_in_item_detail'),

                # Test
                path('test/html/', test_page, name='test_page'),

                # 에러
                path('error/404', error_page, name="error_page"),

                path('', include(router.urls)),
                #autocomplete
                url('autocomplete/menumaster/enterprise_name_ac$', enterprise_name_ac.as_view(), name='enterprise_name_ac'),
                url('autocomplete/menumaster/client_name_ac$', client_name_ac.as_view(), name='client_name_ac'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        # drf yasg
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

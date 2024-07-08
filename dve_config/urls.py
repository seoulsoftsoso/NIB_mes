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
from api.auto_complete import enterprise_name_ac, client_name_ac
from api.base.codemaster_views import CodeMasterViewSet, CodeMasterSelectView


from api.base.enterprise_views import EnterpriseMasterViewSet


from api.base.groupcodemaster_views import GroupCodeMasterViewSet, GenerateCodeMaster
from api.base.menu_config import MenuHandler, getLmenuList, setMenuByUser

from api.base.user_views import UserMasterViewSet, UserMasterSelectViewSet

from api.user.views import CustomObtainAuthToken

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
                path('users/login/', custom_obtain_auth_token),
                re_path(r'^data/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),

                path('dashboard/', dashboard_page, name="dashboard_page"),

                path('basic_information/codemaster/', codemaster),
                path('basic_information/enterprise/', new_enterprise),
                path('basic_information/menumaster/', Menumaster),
                path('basic_information/getlmenulist/', getLmenuList),
                path('basic_information/setmenubyuser/', setMenuByUser.as_view(), name='setmenubyuser'),
                #path('getMenulist/', MenuHandler)
                path('basic_information/user/', UserBasedInfo, name='UserBasedInfo'),
                path('basic_information/dept_mgmt/', DeptMgmt, name='DeptMgmt'),
                path('basic_information/company_mgmt/', CompanyMgmt, name='CompanyMgmt'),
                path('basic_information/item/', item_info, name='item_info'),


                # Item
                path('item/get/', get_item_masters.as_view(), name='get_item_masters'),  # 품목
                path('item/add/', ItemAdd.as_view(), name='ItemAdd'),  # 품목 추가
                path('item/update/', Update_Item.as_view(), name='update_item'),


                # 재고 관리
                path('material/status/', Material_status, name='Material_status'),  # 재고 목록
                path('material/input/', Material_input, name='Material_input'),  # 입고
                path('material/output/', Material_output, name='Material_output'),  # 출고



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

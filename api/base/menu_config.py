from django.db import transaction
from django.db.models.functions import Coalesce
from django.db.models import F, Q
from django.http import JsonResponse
from rest_framework import viewsets, status
from django.views import View

from api.models import MenuMaster, Menu_Auth, UserMaster
from api.serializers import MenuSerializer
from rest_framework.response import Response
from datetime import datetime


# def MenuHandler(self):
#     qs = MenuMaster.objects.filter(menuauth__user_id=self.user.id,
#                                    menuauth__del_flag='N'
#                                    ).annotate(alias=Coalesce('menuauth__alias', F('name'))
#                                               ).values('id', 'code', 'alias', 'path', 'type', 'comment', 'i_class'
#                                                        , 'created_by_id', 'created_at', 'updated_by_id',
#                                                        'updated_at'
#                                                        , 'del_flag').order_by('menuauth__order')
#     menu_list = list(qs)
#
#     return menu_list


class MenuHandler(viewsets.ModelViewSet):
    queryset = MenuMaster.objects.all()
    serializer_class = MenuSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        # 해당 유저의 메뉴 정보 가져오기
        qs = MenuMaster.objects.filter(menuauth__user_id=self.request.user.id,
                                       menuauth__del_flag='N'
                                       ).annotate(alias=Coalesce('menuauth__alias', F('name'))
                                                  ).values('id', 'code', 'alias', 'path', 'type', 'comment', 'i_class'
                                                           , 'created_by_id', 'created_at', 'updated_by_id',
                                                           'updated_at'
                                                           , 'del_flag').order_by('menuauth__order')

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def getLmenuList(request):
    user_id = request.GET.get('user_id')
    client = request.GET.get('client')
    qs = MenuMaster.objects.filter(Q(del_flag='N') | Q(menuauth__del_flag='N')
                                   ).values(
        'id', 'code', 'name', 'type', 'i_class', 'menuauth__id', 'menuauth__alias', 'menuauth__order',
        'menuauth__parent', 'menuauth__menu'
    ).order_by('type').distinct()

    qs_use = qs.filter(menuauth__id__isnull=True)

    qs_use_json = list(qs_use)

    qs_used = qs.filter(menuauth__user=user_id).order_by('menuauth__order')

    qs_used_json = list(qs_used)

    context = {}
    context['useablemenu'] = qs_use_json
    context['usedmenu'] = qs_used_json

    return JsonResponse(context)


class setMenuByUser(View):
    queryset = Menu_Auth.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        menulist = request.POST.getlist('menulist[]', '')
        aliaslist = request.POST.getlist('menunamelist[]', '')
        parentId = request.POST.getlist('parentlist[]', '')
        userId = request.POST.get('user_id', '')

        user = UserMaster.objects.get(id=self.request.user.id)

        client = UserMaster.objects.get(id=userId).id

        # 등록되어 있는 메뉴를 삭제
        self.queryset.filter(user_id=userId).delete()

        cnt = 0
        lcnt = 0

        for index, unit in enumerate(menulist):
            alias = aliaslist[index] if index < len(aliaslist) else None
            parent = int(parentId[index])

            if parent == 0:
                lcnt += 1000
                cnt = lcnt
                parent = None
            else:
                cnt = cnt + 10

            authObj = Menu_Auth.objects.create(
                menu_id=unit,
                alias=alias,
                user_id=userId,
                order=cnt,
                parent_id=parent,
                use_flag='Y',
                del_flag='N',
                created_by=user,
                updated_by=user
            )
            # authObj = Menu_Auth.objects.create(
            #     menu_id=unit,
            #     alias=alias,
            #     user_id=userId,
            #     order=cnt,
            #     use_flag='Y',
            #     del_flag='N'
            # )

            #parent = authObj.id

        return JsonResponse({'error': True, 'message': 'OK'})

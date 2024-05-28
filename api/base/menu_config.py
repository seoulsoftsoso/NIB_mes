from django.db.models.functions import Coalesce
from django.db.models import F
from rest_framework import viewsets

from api.models import MenuMaster
from api.serializers import MenuSerializer
from rest_framework.response import Response


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

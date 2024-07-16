import traceback
import json
from django.contrib.messages import success
from django.db.models import Prefetch, F
from django.db.models.functions import TruncDate
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.db import transaction
from django.utils import timezone
from api.models import Warehouse, ItemInSub, ItemMaster, WarehouseRack, UnitPrice, ItemIn, CustomerMaster


class InputCreate(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            formdata = request.POST
            files = request.FILES

            # 공통 데이터 처리
            location = formdata.get('location_select')  # 위치 : ex) 창고 등
            init_place = formdata.get('init_place_select')  # 거래처
            due_date = formdata.get('due_date')
            # immediately_check = 'on' in formdata.get('immediately_check', []) 추후 어떻게 처리할 지 얘기해야 함

            # JSON 문자열을 파이썬 객체로 변환
            table_data_str = formdata.get('tableData', '[]')
            table_data = json.loads(table_data_str)

            for row in table_data:
                item = ItemMaster.objects.get(id=row['item'])
                warehouse = Warehouse.objects.get(id=location)
                customer = CustomerMaster.objects.get(id=init_place)
                unit = UnitPrice.objects.get(u_item_id=item)
                wr_rack = WarehouseRack.objects.get(warehouse_id=warehouse)

                item_in = ItemIn.objects.create(
                    in_type=row['in_type'],
                    in_status=row['status'],
                    due_date=due_date,  # 입고 예정일
                    in_at=due_date,  # 입고일
                    in_quan=float(row['in_quan']),
                    in_note=row['memo'],
                    in_item=item,
                    wh=warehouse,  # 창고 정보
                    in_custom=customer,  # 거래처 정보
                    uprice=unit,  # 단가
                    wr=wr_rack,
                    created_by_id=request.user.id,
                )

                # 파일 처리
                if f'file_{table_data.index(row)}' in files:
                    item_in.in_image = files[f'file_{table_data.index(row)}']
                    item_in.save()

                # 부분 입고 처리
                if row['status'] == 'P':
                    ItemInSub.objects.create(
                        in_at_sub=due_date,
                        in_quan_sub=float(row['in_quan']),
                        in_etc_sub=row['memo'],
                        in_item=item_in,
                        created_by_id=request.user.id,
                    )

            return JsonResponse({'success': True})

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)

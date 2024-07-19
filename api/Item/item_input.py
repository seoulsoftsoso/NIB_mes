import traceback
import json
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from api.models import Warehouse, ItemInSub, ItemMaster, WarehouseRack, UnitPrice, ItemIn, CustomerMaster
from datetime import datetime


class InputGet(View):
    def get(self, request, *args, **kwargs):
        enterprise = request.user.enterprise_id
        item_id = request.GET.get('item_id')

        item_in = ItemIn.objects.filter(id=item_id, created_by__enterprise_id=enterprise, del_flag='N').select_related(
            'in_custom', 'in_item', 'uprice', 'wh', 'wr'
        ).values('id', 'in_no', 'in_type', 'in_status', 'due_date', 'in_at', 'in_quan', 'in_note', 'in_image', 'created_by',
            'in_item__item_name', 'in_item__item_code', 'in_item__item_detail', 'in_item__standard', 'in_item__model',
            'in_item__unitname', 'in_item__mass', 'in_item__item_type', 'in_item__item_category', 'in_item__current_quan',
            'in_item__safe_quan', 'in_item__qr_code', 'in_item__item_image', 'in_custom__c_name', 'uprice__unit_price',
            'uprice__unit_type', 'wh_id', 'wh__code', 'wh__name', 'wh__region', 'wr_id', 'wr__rack_code', 'wr__rack_name',
            'wr__rack_row', 'wr__rack_line', 'in_custom_id', 'in_item_id'
        )

        result = list(item_in)

        return JsonResponse({
            'result': result
        })


class InputCreate(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        item_in_id = request.POST.get('item_in_id')
        try:
            with transaction.atomic():  # 트랜잭션
                if item_in_id is None:
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

                        in_quan = float(row['in_quan'])

                        item_in = ItemIn.objects.create(
                            in_type=row['in_type'],
                            in_status=row['status'],
                            due_date=due_date,  # 입고 예정일
                            in_at=due_date,  # 입고일
                            in_quan=in_quan,
                            in_note=row['memo'],
                            in_item=item,
                            wh=warehouse,  # 창고 정보
                            in_custom=customer,  # 거래처 정보
                            uprice=unit,  # 단가
                            wr=wr_rack,
                            created_by_id=request.user.id,
                        )

                        # ItemMaster의 current_quan 업데이트
                        item.current_quan += in_quan
                        item.save()

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

                    return JsonResponse({'success': True, 'message': '등록되었습니다.'})

                elif item_in_id is not None:
                    formdata = request.POST
                    files = request.FILES
                    print('formdata', formdata)
                    item_in = ItemIn.objects.get(id=item_in_id)

                    # JSON 문자열을 파이썬 객체로 변환
                    table_data_str = formdata.get('tableData', '[]')
                    table_data = json.loads(table_data_str)[0]  # 첫 번째 항목만 가져옴

                    # 관련 객체들 가져오기
                    item = ItemMaster.objects.get(id=table_data['item'])
                    warehouse = Warehouse.objects.get(id=formdata.get('location_select'))
                    customer = CustomerMaster.objects.get(id=formdata.get('init_place_select'))
                    unit = UnitPrice.objects.get(u_item_id=item)
                    wr_rack = WarehouseRack.objects.get(warehouse_id=warehouse)

                    # ItemMaster의 current_quan 업데이트 (기존 수량과의 차이만큼 조정)
                    # quantity_difference = float(table_data['in_quan']) - item_in.in_quan
                    item.current_quan += float(table_data['in_quan'])
                    item.save()

                    # ItemIn 객체 업데이트
                    item_in.in_type = table_data['in_type']
                    item_in.in_status = table_data['status']
                    item_in.due_date = formdata.get('due_date')
                    item_in.in_at = formdata.get('due_date')
                    item_in.in_quan = float(table_data['in_quan'])
                    item_in.in_note = table_data['memo']
                    item_in.in_item = item
                    item_in.wh = warehouse
                    item_in.in_custom = customer
                    item_in.uprice = unit
                    item_in.wr = wr_rack
                    item_in.save()

                    # 파일 처리
                    if 'file_0' in files:
                        item_in.in_image = files['file_0']
                        item_in.save()

                    # 부분 입고 처리
                    if table_data['status'] == 'P':
                        ItemInSub.objects.filter(in_item=item_in).delete()  # 기존 부분 입고 기록 삭제

                        ItemInSub.objects.create(
                            in_at_sub=formdata.get('due_date'),
                            in_quan_sub=float(table_data['in_quan']),
                            in_etc_sub=table_data['memo'],
                            in_item=item_in,
                            created_by_id=request.user.id,
                        )

                    return JsonResponse({'success': True, 'message': '변경사항이 저장되었습니다.'})

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


class InputUpdate(View):
    def post(self, request, *args, **kwargs):
        try:
            type = request.POST.get('type')
            if type == 'D':

                item_ids = request.POST.getlist('item_id[]')

                with transaction.atomic():
                    updated_count = ItemIn.objects.filter(id__in=item_ids).update(del_flag='Y')

                return JsonResponse({'success': True, 'message': f'{updated_count}개의 항목이 성공적으로 삭제되었습니다.'})

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


class ItemInFilter(View):
    def get(self, request, *args, **kwargs):
        qs = ItemIn.objects.filter(created_by__enterprise_id=request.user.enterprise_id, del_flag="N")

        # 입고 상태 필터
        item_in_filter = request.GET.get('item_in_filter')
        if item_in_filter:
            statuses = item_in_filter.split(',')
            qs = qs.filter(in_status__in=statuses)

        # 아이템 유형 필터
        item_type_filter = request.GET.get('item_type_filter')
        if item_type_filter:
            types = item_type_filter.split(',')
            qs = qs.filter(in_item__item_type__in=types)

        # 위치(창고) 필터
        warehouse_filter = request.GET.get('warehouse_filter')
        if warehouse_filter:
            warehouses = warehouse_filter.split(',')
            qs = qs.filter(wh_id__in=warehouses)

        # 날짜 범위 필터
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            qs = qs.filter(in_at__date__range=[start_date, end_date])
        elif start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            qs = qs.filter(in_at__date__gte=start_date)
        elif end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            qs = qs.filter(in_at__date__lte=end_date)

        qs = qs.select_related('in_item', 'in_custom', 'uprice', 'wh')

        # values 메소드는 get_display() 메소드에 접근 못함 수동으로 값을 추가해야 됌
        result = []
        for item in qs:
            item_dict = model_to_dict(item, fields=[
                'id', 'in_status', 'due_date', 'in_no', 'in_quan', 'due_date'
            ])
            item_dict.update({
                'in_status_display': item.get_in_status_display(),
                'in_custom__c_name': item.in_custom.c_name if item.in_custom else '',
                'in_item__item_code': item.in_item.item_code if item.in_item else '',
                'in_item__item_name': item.in_item.item_name if item.in_item else '',
                'in_item__item_type': item.in_item.get_item_type_display() if item.in_item else '',
                'in_item__mass': item.in_item.mass if item.in_item else '',
                'in_item__unitname': item.in_item.unitname if item.in_item else '',
                'uprice__unit_price': item.uprice.unit_price if item.uprice else '',
                'wh__name': item.wh.name if item.wh else '',
            })
            result.append(item_dict)

        return JsonResponse({
            'result': result
        })

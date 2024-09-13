import traceback
import json

from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from api.models import Warehouse, ItemInSub, ItemMaster, WarehouseRack, UnitPrice, ItemIn, CustomerMaster, ItemOut, \
    StockStatus
from datetime import datetime


class OutputGet(View):
    def get(self, request, *args, **kwargs):
        enterprise = request.user.enterprise_id
        item_id = request.GET.get('item_id')

        item_out = ItemOut.objects.filter(id=item_id, created_by__enterprise_id=enterprise, del_flag='N').select_related(
            'out_custom', 'out_item', 'out_uprice', 'out_wh', 'out_wr'
        ).values('id', 'out_no', 'out_type', 'out_status', 'out_date', 'out_at', 'out_quan', 'out_note', 'out_image', 'created_by',
            'out_item__item_name', 'out_item__item_code', 'out_item__item_detail', 'out_item__standard', 'out_item__model',
            'out_item__unitname', 'out_item__mass', 'out_item__item_type', 'out_item__item_category', 'out_item__current_quan',
            'out_item__safe_quan', 'out_item__qr_code', 'out_item__item_image', 'out_custom__c_name', 'out_uprice__unit_price',
            'out_uprice__unit_type', 'out_wh_id', 'out_wh__code', 'out_wh__name', 'out_wh__region', 'out_wr_id', 'out_wr__rack_code', 'out_wr__rack_name',
            'out_wr__rack_row', 'out_wr__rack_line', 'out_custom_id', 'out_item_id'
        )

        result = list(item_out)

        return JsonResponse({
            'result': result
        })


class OutputCreate(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        item_out_id = request.POST.get('item_out_id')
        try:
            with transaction.atomic():  # 트랜잭션
                if item_out_id is None:
                    formdata = request.POST
                    files = request.FILES

                    # 공통 데이터 처리
                    location = formdata.get('location_select')  # 위치 : ex) 창고 등
                    init_place = formdata.get('init_place_select')  # 거래처
                    out_date = formdata.get('out_date')
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

                        out_quan = float(row['out_quan'])

                        item_out = ItemOut.objects.create(
                            out_type=row['out_type'],
                            out_status=row['status'],
                            out_date=out_date,  # 입고 예정일
                            out_at=out_date,  # 입고일
                            out_quan=out_quan,
                            out_note=row['memo'],
                            out_item=item,
                            out_wh=warehouse,  # 창고 정보
                            out_custom=customer,  # 거래처 정보
                            out_uprice=unit,  # 단가
                            out_wr=wr_rack,
                            created_by_id=request.user.id,
                        )

                        # 재고 현황 모델 update
                        StockStatus.objects.create(
                            item=item,
                            wh=warehouse,
                            wr=wr_rack,
                            enterprise_id=request.user.enterprise_id,
                            output=item_out,
                            quantity=out_quan,
                            io_status='O',
                            created_by_id=request.user.id,
                        )

                        # ItemMaster의 current_quan 업데이트
                        item.current_quan -= out_quan
                        item.save()

                        # StockStatus(재고 현황)에 데이터 저장 또는 업데이트
                        stock_status, created = StockStatus.objects.get_or_create(
                            item=item,
                            wh=warehouse,
                            wr=wr_rack,
                            enterprise_id=request.user.enterprise_id,
                            defaults={
                                'quantity': out_quan,
                                'io_status': 'I',
                                'created_by_id': request.user.id,
                                'output': out_quan
                            }
                        )

                        if not created:
                            stock_status.quantity -= out_quan
                            stock_status.save()

                        # 파일 처리
                        if f'file_{table_data.index(row)}' in files:
                            item_out.in_image = files[f'file_{table_data.index(row)}']
                            item_out.save()

                        # 부분 입고 처리
                        if row['status'] == 'P':
                            ItemInSub.objects.create(
                                in_at_sub=out_date,
                                in_quan_sub=float(row['in_quan']),
                                in_etc_sub=row['memo'],
                                in_item=item_out,
                                created_by_id=request.user.id,
                            )

                    return JsonResponse({'success': True, 'message': '등록되었습니다.'})

                elif item_out_id is not None:
                    formdata = request.POST
                    files = request.FILES
                    print('formdata', formdata)
                    item_out = ItemOut.objects.get(id=item_out_id)

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
                    item.current_quan -= float(table_data['out_quan'])
                    item.save()

                    # ItemIn 객체 업데이트
                    item_out.in_type = table_data['out_type']
                    item_out.in_status = table_data['status']
                    item_out.due_date = formdata.get('out_date')
                    item_out.in_at = formdata.get('out_date')
                    item_out.in_quan = float(table_data['out_quan'])
                    item_out.in_note = table_data['memo']
                    item_out.in_item = item
                    item_out.wh = warehouse
                    item_out.in_custom = customer
                    item_out.uprice = unit
                    item_out.wr = wr_rack
                    item_out.save()

                    # StockStatus 업데이트
                    stock_status = StockStatus.objects.get(input_id=item_out_id)
                    stock_status.quantity = float(table_data['out_quan'])
                    stock_status.item = item
                    stock_status.wh = warehouse
                    stock_status.wr = wr_rack
                    stock_status.save()

                    # 파일 처리
                    if 'file_0' in files:
                        item_out.in_image = files['file_0']
                        item_out.save()

                    # 부분 입고 처리
                    if table_data['status'] == 'P':
                        ItemInSub.objects.filter(in_item=item_out).delete()  # 기존 부분 입고 기록 삭제

                        ItemInSub.objects.create(
                            in_at_sub=formdata.get('due_date'),
                            in_quan_sub=float(table_data['in_quan']),
                            in_etc_sub=table_data['memo'],
                            in_item=item_out,
                            created_by_id=request.user.id,
                        )

                    return JsonResponse({'success': True, 'message': '변경사항이 저장되었습니다.'})

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


class OutputUpdate(View):
    def post(self, request, *args, **kwargs):
        try:
            type = request.POST.get('type')
            if type == 'D':

                item_ids = request.POST.getlist('item_id[]')

                with transaction.atomic():
                    updated_count = ItemOut.objects.filter(id__in=item_ids).update(del_flag='Y')

                return JsonResponse({'success': True, 'message': f'{updated_count}개의 항목이 성공적으로 삭제되었습니다.'})

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


class ItemOutFilter(View):
    def get(self, request, *args, **kwargs):
        qs = ItemOut.objects.filter(created_by__enterprise_id=request.user.enterprise_id, del_flag="N")

        # 출고 상태 필터
        item_out_filter = request.GET.get('item_out_filter')
        if item_out_filter:
            statuses = item_out_filter.split(',')
            qs = qs.filter(out_status__in=statuses)

        # 아이템 유형 필터
        item_type_filter = request.GET.get('item_type_filter')
        if item_type_filter:
            types = item_type_filter.split(',')
            qs = qs.filter(out_item__item_type__in=types)

        # 위치(창고) 필터
        warehouse_filter = request.GET.get('warehouse_filter')
        if warehouse_filter:
            warehouses = warehouse_filter.split(',')
            qs = qs.filter(out_wh_id__in=warehouses)

        # 날짜 범위 필터
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            qs = qs.filter(out_at__date__range=[start_date, end_date])
        elif start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            qs = qs.filter(out_at__date__gte=start_date)
        elif end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            qs = qs.filter(out_at__date__lte=end_date)

        # 품목번호 또는 품목명 필터
        product_name_num = request.GET.get('product_name_num')
        if product_name_num:
            qs = qs.filter(
                Q(out_item__item_code__icontains=product_name_num) |
                Q(out_item__item_name__icontains=product_name_num)
            )

        # 입고번호 또는 입고처명 필터
        location_input = request.GET.get('location_input')
        if location_input:
            qs = qs.filter(
                Q(out_no__icontains=location_input) |
                Q(out_custom__c_name__icontains=location_input)
            )

        qs = qs.select_related('out_item', 'out_custom', 'out_uprice', 'out_wh')

        # values 메소드는 get_display() 메소드에 접근 못함 수동으로 값을 추가해야 됌
        result = []
        for item in qs:
            item_dict = model_to_dict(item, fields=[
                'id', 'out_status', 'out_date', 'out_no', 'out_quan'
            ])
            item_dict.update({
                'out_status_display': item.get_out_status_display(),
                'out_custom__c_name': item.out_custom.c_name if item.out_custom else '',
                'out_item__item_code': item.out_item.item_code if item.out_item else '',
                'out_item__item_name': item.out_item.item_name if item.out_item else '',
                'out_item__item_type': item.out_item.get_item_type_display() if item.out_item else '',
                'out_item__mass': item.out_item.mass if item.out_item else '',
                'out_item__unitname': item.out_item.unitname if item.out_item else '',
                'out_uprice__unit_price': item.out_uprice.unit_price if item.out_uprice else '',
                'out_wh__name': item.out_wh.name if item.out_wh else '',
            })
            result.append(item_dict)

        return JsonResponse({
            'result': result
        })

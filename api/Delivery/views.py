import traceback
import json
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from api.models import Warehouse, ItemInSub, ItemMaster, WarehouseRack, UnitPrice, ItemIn, CustomerMaster, ItemOut, \
    StockStatus, DeliveryMaster
from msgs import msg_del_ok


class DeliveryGet(View):
    def post(self, request, *args, **kwargs):
        # 클라이언트로부터 받은 파라미터
        draw = int(request.POST.get('draw', 1))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))
        search_value = request.POST.get('search[value]', '')
        order_column = request.POST.get('order[0][column]', 0)
        order_dir = request.POST.get('order[0][dir]', 'asc')

        # 추가 필터링 파라미터
        search_input = request.POST.get('search_input', '')
        del_status = request.POST.get('del_status', '')
        del_method = request.POST.get('del_method', '')
        daterange = request.POST.get('daterange', '')

        # 쿼리셋 초기화
        queryset = DeliveryMaster.objects.filter(del_flag='N', created_by__enterprise_id=request.user.enterprise_id).select_related('customer', 'item_out')

        # 검색 조건 적용
        if search_input:
            queryset = queryset.filter(
                Q(no__icontains=search_input) |
                Q(invoice_num__icontains=search_input) |
                Q(customer__c_name__icontains=search_input) |
                Q(item_out__out_item__item_name__icontains=search_input)
            )

        # 상태 필터 적용
        # if del_status:
        #     queryset = queryset.filter(출하상태=del_status)

        # 출하 방법 필터 적용
        if del_method:
            queryset = queryset.filter(출하방법=del_method)

        # 날짜 범위 필터 적용
        if daterange:
            start_date, end_date = daterange.split(' - ')
            queryset = queryset.filter(due_date__range=[start_date, end_date])

        # 정렬
        columns = ['due_date', 'no', 'customer__c_name', 'item_out__out_item__item_name', 'status', 'del_price',
                   'item_out__out_type', 'del_company', 'invoice_num']
        if order_column and order_dir:
            order_column = columns[int(order_column)]
            if order_dir == 'desc':
                order_column = '-' + order_column
            queryset = queryset.order_by(order_column)

        # 전체 레코드 수
        total_records = queryset.count()

        # 페이징
        paginator = Paginator(queryset, length)
        page = (start // length) + 1
        data = paginator.page(page)

        # 데이터 포맷팅
        formatted_data = []
        for item in data.object_list:
            delivery_method = '택배' if item.del_company and item.invoice_num else '직접수령'
            formatted_data.append({
                'due_date': item.due_date,
                'no': item.no,
                'customer': item.customer.c_name if item.customer else '',
                'item': item.item_out.out_item.item_name if item.item_out and item.item_out.out_item else '',
                'quantity': item.item_out.out_quan,
                'del_price': item.del_price,
                'delivery_method': delivery_method,
                'id': item.id,
                'del_company': item.del_company.com_name if item.del_company else '',
                'del_company_id': item.del_company.com_id if item.del_company else '',
                'invoice_num': item.invoice_num
            })

        # 응답 데이터 구성
        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': formatted_data
        }

        return JsonResponse(response)


class DeliveryCreate(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        delivery_id = request.POST.get('delivery_hidden_id')
        try:
            with transaction.atomic():  # 트랜잭션
                if delivery_id is None:
                    formdata = request.POST
                    print('del_form', formdata)

                    # 공통 데이터 처리
                    init_place = formdata.get('init_place_select')  # 거래처
                    out_date = formdata.get('out_date')
                    # immediately_check = 'on' in formdata.get('immediately_check', []) 추후 어떻게 처리할 지 얘기해야 함

                    # JSON 문자열을 파이썬 객체로 변환
                    table_data_str = formdata.get('tableData', '[]')
                    table_data = json.loads(table_data_str)

                    for row in table_data:
                        out_no = ItemOut.objects.get(id=row['item'])

                        DeliveryMaster.objects.create(
                            due_date=out_date,
                            no=out_no.out_no,
                            del_company_id=row.get('del_com_select'),
                            del_price=row.get('del_price'),
                            invoice_num=row.get('invoice_num'),
                            item_out_id=row.get('item'),
                            customer_id=init_place,
                            created_by_id=request.user.id,
                        )

                    return JsonResponse({'success': True, 'message': '등록되었습니다.'})

                elif delivery_id is not None:
                    formdata = request.POST
                    print('formdata', formdata)
                    delivery = DeliveryMaster.objects.get(id=delivery_id)

                    # JSON 문자열을 파이썬 객체로 변환
                    table_data_str = formdata.get('tableData', '[]')
                    table_data = json.loads(table_data_str)[0]  # 첫 번째 항목만 가져옴

                    # 관련 객체들 가져오기
                    item_out = ItemOut.objects.get(id=table_data['item'])
                    customer = CustomerMaster.objects.get(id=formdata.get('init_place_select'))

                    # Delivery 객체 업데이트
                    delivery.customer = customer
                    delivery.due_date = formdata.get('out_date')
                    delivery.del_price = table_data['del_price']
                    delivery.del_company_id = table_data['del_com_select']
                    delivery.invoice_num = table_data['invoice_num']
                    delivery.item_out = item_out
                    delivery.save()

                    return JsonResponse({'success': True, 'message': '변경사항이 저장되었습니다.'})

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


class InvoiceGet(View):
    def get(self, request, *args, **kwargs):

        delivery_id = request.GET.get('delivery_id')

        delivery_qs = DeliveryMaster.objects.filter(del_flag='N', created_by__enterprise_id=request.user.enterprise_id,
                                                    id=delivery_id).select_related('customer', 'item_out')

        result_data = []
        for item in delivery_qs:
            result_data.append({
                'seller_business_num': item.created_by.enterprise.licensee_number,
                'seller_enterprise_name': item.created_by.enterprise.name,
                'seller_address': item.created_by.enterprise.address,
                'seller_tel': item.created_by.enterprise.office_phone,
                'buyer_business_num': item.customer.business_num,
                'buyer_enterprise_name': item.customer.c_name,
                'buyer_address': item.customer.address,
                'buyer_tel': item.customer.official_tel,
                'item_name': item.item_out.out_item.item_name,
                'out_quan': item.item_out.out_quan,
                'unit_price': item.item_out.out_uprice.unit_price,
                'out_no': item.item_out.out_no,
                'del_price': item.del_price,
                'customer': item.customer_id,
                'due_date': item.due_date,
                'item_out': item.item_out.id,
                'del_company': item.del_company_id,
                'invoice_num': item.invoice_num,
                'delivery_id': item.id,
            })

        return JsonResponse({'result': result_data})


class UpdateDelivery(View):
    def post(self, request, *args, **kwargs):
        delivery = DeliveryMaster.objects.get(id=request.POST.get('delivery_id'))

        delivery.del_flag = 'Y'
        delivery.save()

        return JsonResponse({'success': True, 'message': msg_del_ok})

import traceback
import qrcode
import io
import uuid

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Prefetch, F, Max, Q
from django.db.models.functions import TruncDate
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.db import models
from api.models import ItemMaster, UnitPrice, StockStatus
from dve_config import settings


def get_item_data(item_id=None, enterprise_id=None):
    query = ItemMaster.objects.filter(del_flag="N", enterprise_id=enterprise_id).prefetch_related(
        Prefetch('unit_prise_item', queryset=UnitPrice.objects.filter(del_flag="N"), to_attr='unit_prices')
    ).annotate(
        item_type_display=F('item_type'),
        unit_type=F('unit_prise_item__unit_type'),
        created_date=TruncDate('created_at')
    )

    if item_id is not None:
        query = query.filter(id=item_id)

    items = query.values(
        'id', 'item_code', 'item_name', 'item_detail', 'standard', 'created_date',
        'model', 'unitname', 'mass', 'item_category', 'current_quan',
        'safe_quan', 'color', 'qr_code', 'item_image', 'item_type_display',
        'unit_type', 'unit_prise_item__unit_price'
    )

    # CHOICES 값 변환 및 날짜 형식 변경
    for item in items:
        item['item_type_display'] = dict(ItemMaster.ITEM_TYPE_CHOICES).get(item['item_type_display'], '')
        item['unit_type_display'] = dict(UnitPrice.UNIT_TYPE_CHOICES).get(item['unit_type'], '')
        item['created_at'] = item['created_date'].strftime('%Y-%m-%d')

    result = list(items)

    # 단일 항목 요청 시 첫 번째 항목만 반환
    if item_id is not None and result:
        return result[0]

    return result


class get_item_masters(View):
    def get(self, request, *args, **kwargs):
        enterprise = request.user.enterprise_id
        items = get_item_data(enterprise_id=enterprise)
        context = {'results': items}
        return JsonResponse(context, safe=False)


class get_one_item_masters(View):
    def get(self, request, *args, **kwargs):
        enterprise = request.user.enterprise_id
        item_id = request.GET.get('item_id', None)
        one_item = get_item_data(item_id=item_id, enterprise_id=enterprise)
        context = {'results': one_item}
        return JsonResponse(context, safe=False)


class GetStock(View):
    def post(self, request, *args, **kwargs):
        enterprise = request.user.enterprise_id
        draw = int(request.POST.get('draw', 1))
        start = int(request.POST.get('start', 0))
        length = int(request.POST.get('length', 10))

        # 최신 데이터를 가져오기 위해 서브쿼리 사용
        latest_stock = StockStatus.objects.filter(
            del_flag="N",
            enterprise_id=enterprise
        ).values('item', 'wh').annotate(
            latest_id=Max('id')
        ).values('latest_id')

        # 기본 쿼리셋
        queryset = StockStatus.objects.filter(
            id__in=latest_stock
        ).select_related('item', 'wh', 'wr', 'input').order_by('-id')

        # 검색 기능 구현
        search_value = request.POST.get('search[value]', '')
        if search_value:
            queryset = queryset.filter(
                Q(item__item_code__icontains=search_value) |
                Q(item__item_name__icontains=search_value) |
                Q(wh__name__icontains=search_value)
            )

        # 정렬 기능 구현
        order_column_index = request.POST.get('order[0][column]', '')
        order_dir = request.POST.get('order[0][dir]', 'asc')
        if order_column_index:
            order_column = request.POST.get(f'columns[{order_column_index}][data]', '')
            # DataTables 열 이름을 Django 모델 필드 이름으로 매핑
            column_map = {
                'item_code': 'item__item_code',
                'item_name': 'item__item_name',
                'item_type': 'item__item_type',
                'item_img': 'item__item_image',
                'unitname': 'item__unitname',
                'quantity': 'quantity',
                'in_type': 'input__in_type',
                'unit_price': 'input__uprice__unit_price',
                'wh_name': 'wh__name',
                'created_at': 'item__created_at',
            }
            order_column = column_map.get(order_column, order_column)
            if order_column:
                if order_dir == 'desc':
                    order_column = f'-{order_column}'
                queryset = queryset.order_by(order_column)

        total = queryset.count()

        # 페이징
        data = queryset[start:start + length]

        result = []
        for item in data:
            in_type = item.input.get_in_type_display() if item.input else ''
            out_type = item.output.get_out_type_display() if item.output else ''

            # uprice_type 및 unit_price 처리
            if item.input and item.input.uprice:
                uprice_type = item.input.uprice.get_unit_type_display()
                unit_price = item.input.uprice.unit_price
            elif item.output and item.output.out_uprice:
                uprice_type = item.output.out_uprice.get_unit_type_display()
                unit_price = item.output.out_uprice.unit_price
            else:
                uprice_type = ''
                unit_price = None

            # item_img 처리
            item_img = item.item.item_image.url if item.item.item_image else ''

            result.append({
                'id': item.id,
                'item_id': item.item.id,
                'item_code': item.item.item_code,
                'item_name': item.item.item_name,
                'item_type': item.item.get_item_type_display(),
                'unitname': item.item.unitname,
                'current_quan': item.item.current_quan,
                'quantity': item.quantity,
                'wh_name': item.wh.name,
                'wh': item.wh.id,
                'in_type': in_type,
                'out_type': out_type,
                'unit_price': unit_price,
                'standard': item.item.standard,
                'model': item.item.model,
                'category': item.item.item_category,
                'uprice_type': uprice_type,
                'item_img': item_img,
                'created_at': item.item.created_at.strftime('%Y-%m-%d') if item.item.created_at else ''
            })

        return JsonResponse({
            'draw': draw,
            'recordsTotal': total,
            'recordsFiltered': total,
            'data': result,
        })


class ItemAdd(View):

    def generate_qr_code(self, item_id):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        url = f"{settings.BASE_URL}/qr_code/item_detail/{item_id}/"
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')

        file_name = f'{uuid.uuid4()}.png'
        file_content = ContentFile(buffer.getvalue(), name=file_name)

        return file_content

    def post(self, request, *args, **kwargs):
        formdata = request.POST
        file_path = request.FILES.get('item_image')
        action = formdata.get('action')

        try:
            if action == 'create':

                item = ItemMaster(
                    item_name=formdata.get('item_name'),
                    item_code=formdata.get('item_code'),
                    item_type=formdata.get('item_type'),
                    item_category=formdata.get('item_category'),
                    model=formdata.get('item_model'),
                    standard=formdata.get('item_standard'),
                    unitname=formdata.get('unitname'),
                    current_quan=0,
                    safe_quan=formdata.get('safe_quan') or None,
                    created_by_id=request.user.id,
                    enterprise_id=request.user.enterprise_id,
                )
                if file_path:
                    item.item_image = file_path

                item.save()

                unit_price = item.unit_prise_item.create(
                    unit_price=formdata.get('item_unit_price'),
                    unit_type=formdata.get('unit_type'),
                    created_by_id=request.user.id,
                )

                # QR 코드 이미지 생성 및 저장
                qr_code_file = self.generate_qr_code(item.id)
                item.qr_code.save(qr_code_file.name, qr_code_file, save=True)

            elif action == 'update':
                item_id = formdata.get('item_id')
                item = ItemMaster.objects.get(id=item_id)
                item.item_name = formdata.get('item_name')
                item.qr_code = formdata.get('item_barcode', '')
                item.item_code = formdata.get('item_code')
                item.item_type = formdata.get('item_type')
                item.item_category = formdata.get('item_category')
                item.model = formdata.get('item_model')
                item.standard = formdata.get('item_standard')
                item.unitname = formdata.get('unitname')
                item.current_quan = formdata.get('quan') or None
                item.safe_quan = formdata.get('safe_quan') or None

                if file_path:
                    item.item_image = file_path
                item.save()

                unit_prices = item.unit_prise_item.filter(del_flag='N')
                if unit_prices.exists():
                    unit_price = unit_prices.first()
                    unit_price.unit_price = formdata.get('item_unit_price')
                    unit_price.updated_by = request.user
                    unit_price.save()
                else:
                    unit_price = item.unit_prise_item.create(
                        unit_price=formdata.get('item_unit_price'),
                        updated_by_id=request.user.id,
                    )

            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)

            # 아이템 정보를 딕셔너리로 변환
            item_data = model_to_dict(item)

            # FieldFile 객체 처리
            for field in item._meta.fields:
                if isinstance(field, models.FileField):
                    file_field = getattr(item, field.name)
                    if file_field:
                        item_data[field.name] = file_field.url
                    else:
                        item_data[field.name] = None

            unit_price_obj = item.unit_prise_item.filter(del_flag='N').first()
            if unit_price_obj:
                item_data['unit_price'] = unit_price_obj.unit_price
                item_data['unit_type'] = unit_price_obj.unit_type
                item_data['unit_type_display'] = unit_price_obj.get_unit_type_display()
            else:
                item_data['unit_price'] = None
                item_data['unit_type'] = None
                item_data['unit_type_display'] = None

            # 파일 이름 추가
            if item.item_image:
                item_data['file_name'] = item.item_image.name.split('/')[-1]
            else:
                item_data['file_name'] = ''

            message = '수정되었습니다.' if action == 'update' else '등록되었습니다.'
            return JsonResponse({
                'message': message,
                'qr_code': item.qr_code.url if item.qr_code else None,
                'item': item_data
            })

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


class Update_Item(View):

    def post(self, request, *args, **kwargs):
        type = request.POST.get('type')
        print('FILES', request.FILES)
        if type == 'E':
            try:
                item = get_object_or_404(ItemMaster, id=request.POST.get('item_id'))

                item.item_name = request.POST.get('품목명', item.item_name)
                item.item_code = request.POST.get('품목코드', item.item_code)
                item.standard = request.POST.get('규격', item.standard)
                item.model = request.POST.get('모델', item.model)
                item.item_type = request.POST.get('품목유형', item.item_type)
                item.item_category = request.POST.get('카테고리', item.item_category)
                item.current_quan = request.POST.get('현재수량', item.current_quan)
                item.safe_quan = request.POST.get('안전재고', item.safe_quan)

                # QR 코드 필드 처리
                if 'QR 코드' in request.POST:
                    item.qr_code = request.POST.get('QR 코드')

                # 이미지 업데이트
                if 'item_image' in request.FILES:
                    item.item_image = request.FILES['item_image']

                item.save()

                unit_prices = item.unit_prise_item.filter(del_flag='N')
                unit_type_displays = [price.get_unit_type_display() for price in unit_prices]

                return JsonResponse({
                    'message': 'success',
                    'item_code': item.item_code,
                    'item_name': item.item_name,
                    'standard': item.standard,
                    'model': item.model,
                    'item_type': item.get_item_type_display(),
                    'item_category': item.item_category,
                    'current_quan': item.current_quan,
                    'safe_quan': item.safe_quan,
                    'qr_code': item.qr_code.url if item.qr_code else None,  # URL로 변환
                    'unitname': item.unitname,
                    'item_image': item.item_image.url if item.item_image else None,
                    'unit_type_displays': unit_type_displays
                })
            except Exception as e:
                print(f"Error: {str(e)}")
                print(traceback.format_exc())
                return JsonResponse({'message': f'Error: {str(e)}'}, status=400)

        elif type == "D":
            try:
                item = get_object_or_404(ItemMaster, id=request.POST.get('item_id'))
                item.del_flag = "Y"
                item.save()

                return JsonResponse({'success': True})
            except Exception as e:
                print(f"Error: {str(e)}")
                print(traceback.format_exc())
                return JsonResponse({'message': f'Error: {str(e)}'}, status=400)
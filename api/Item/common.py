import traceback

from django.contrib.messages import success
from django.db.models import Prefetch, F
from django.db.models.functions import TruncDate
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.db import models
from api.models import ItemMaster, UnitPrice


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


class ItemAdd(View):

    def post(self, request, *args, **kwargs):
        formdata = request.POST
        file_path = request.FILES.get('item_image')
        action = formdata.get('action')

        try:
            if action == 'create':
                item = ItemMaster(
                    item_name=formdata.get('item_name'),
                    qr_code=formdata.get('item_barcode', ''),
                    item_code=formdata.get('item_code'),
                    item_type=formdata.get('item_type'),
                    item_category=formdata.get('item_category'),
                    model=formdata.get('item_model'),
                    standard=formdata.get('item_standard'),
                    current_quan=formdata.get('quan') or None,
                    safe_quan=formdata.get('safe_quan') or None,
                    created_by_id=request.user.id,
                )
                if file_path:
                    item.item_image = file_path
                item.save()

                unit_price = item.unit_prise_item.create(
                    unit_price=formdata.get('item_unit_price'),
                    created_by_id=request.user.id,
                )

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
                'item': item_data
            })

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)


class Update_Item(View):

    def post(self, request, *args, **kwargs):
        type = request.POST.get('type')
        print('type', type)
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
                item.qr_code = request.POST.get('QR 코드', item.qr_code)

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
                    'qr_code': item.qr_code,
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
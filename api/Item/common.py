import traceback

from django.contrib.messages import success
from django.db.models import Prefetch, F
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from api.models import ItemMaster, UnitPrice


def get_item_data(item_id=None):
    query = ItemMaster.objects.filter(del_flag="N").prefetch_related(
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
        items = get_item_data()
        context = {'results': items}
        return JsonResponse(context, safe=False)


class get_one_item_masters(View):
    def get(self, request, *args, **kwargs):
        item_id = request.GET.get('item_id', None)
        one_item = get_item_data(item_id)
        context = {'results': one_item}
        return JsonResponse(context, safe=False)


class ItemAdd(View):

    def post(self, request, *args, **kwargs):

        formdata = request.POST
        file_path = request.FILES.get('item_image')
        print(formdata)

        try:

            item = ItemMaster(
                item_name=formdata.get('item_name'),
                qr_code=formdata.get('item_barcode', ''),
                item_code=formdata.get('item_code'),
                item_type=formdata.get('item_type'),
                # item_unit_price=formdata.get('item_unit_price'),
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

        except Exception as e:
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': str(e)}, status=400)

        return JsonResponse({'message': 'success'})


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
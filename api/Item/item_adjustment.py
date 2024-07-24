from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.models import ItemIn


@csrf_exempt
def get_material_data(request):
    enterprise = request.user.enterprise_id
    draw = int(request.POST.get('draw', 1))
    start = int(request.POST.get('start', 0))
    length = int(request.POST.get('length', 10))

    # 기본 쿼리셋
    queryset = ItemIn.objects.filter(
        created_by__enterprise_id=enterprise,
        del_flag='N'
    ).select_related('in_custom', 'in_item', 'uprice', 'wh', 'wr')

    # 검색 기능 구현
    search_value = request.POST.get('search[value]', '')
    if search_value:
        queryset = queryset.filter(
            Q(in_no__icontains=search_value) |
            Q(in_custom__c_name__icontains=search_value) |
            Q(in_item__item_name__icontains=search_value)
        )

    # 정렬 기능 구현
    order_column_index = request.POST.get('order[0][column]', '')
    print('index', order_column_index)
    order_dir = request.POST.get('order[0][dir]', 'asc')
    if order_column_index:
        order_column = request.POST.get(f'columns[{order_column_index}][data]', '')
        if order_column:
            if order_dir == 'desc':
                order_column = f'-{order_column}'
            queryset = queryset.order_by(order_column)

    total = queryset.count()

    # 페이징
    data = queryset[start:start + length]

    result = []
    for item in data:
        result.append({
            'id': item.id,
            'in_status': item.get_in_status_display(),
            'due_date': item.due_date.strftime('%Y-%m-%d') if item.due_date else '',
            'in_no': item.in_no,
            'in_custom__c_name': item.in_custom.c_name,
            'in_item': {
                'item_code': item.in_item.item_code,
                'item_name': item.in_item.item_name,
                'item_type': item.in_item.get_item_type_display(),
                'unitname': item.in_item.unitname,
                'current_quan': item.in_item.current_quan,

            },
            'in_type': item.get_in_type_display(),
            'in_quan': item.in_quan,
            'uprice': item.uprice.unit_price,
            'wh_name': item.wh.name,
        })

        print('res', result)

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': total,
        'data': result,
    })

import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from api.models import DeliveryCompany


def DeliveryList(request):  # 택배사 조회
    track_response = requests.post(
      url="https://apis.tracker.delivery/graphql",
      headers={
        # Instructions for obtaining [YOUR_CLIENT_ID] and [YOUR_CLIENT_SECRET] can be found in the documentation below:
        # See: https://tracker.delivery/docs/authentication
        "Authorization": "TRACKQL-API-KEY 134sr1s6a8aa4e43sr69t0faps:1k7fr3ieqnmltea40313frpk0ei06d6ckonoefjheehl69t4hi0q",
         "Accept-Language": "ko-KR",
      },
      json={
        "query": """
        query Carriers(
          $cursor: String,
          $countryCode: String,
          $searchText: String
        ) {
          carriers(
            first: 20,
            after: $cursor,
            countryCode: $countryCode,
            searchText: $searchText
          ) {
            edges {
              node {
                id
                name
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """.strip(),
        "variables": {
          "cursor": None,
          "countryCode": None,
          "searchText": None
        },
      }
    ).json()

    print(track_response)
    result = track_response['data']['carriers']['edges']

    for edge in result:
        carrier_id = edge['node']['id']
        carrier_name = edge['node']['name']

        # 중복 체크 후 저장
        if not DeliveryCompany.objects.filter(com_id=carrier_id).exists():
            DeliveryCompany.objects.create(com_id=carrier_id, com_name=carrier_name)

    return JsonResponse({'result': result})


def DeliveryTrack(request):  # 운송장 정보 조회
    del_com_id = request.GET.get('del_com_id')
    invoice_num = request.GET.get('invoice_num')
    try:
        track_response = requests.post(
            url="https://apis.tracker.delivery/graphql",
            headers={
                # Instructions for obtaining [YOUR_CLIENT_ID] and [YOUR_CLIENT_SECRET] can be found in the documentation below:
                # See: https://tracker.delivery/docs/authentication
                "Authorization": "TRACKQL-API-KEY 134sr1s6a8aa4e43sr69t0faps:1k7fr3ieqnmltea40313frpk0ei06d6ckonoefjheehl69t4hi0q",
                "Accept-Language": "ko-KR",
            },
            json={
                "query": """
                query Track(
                  $carrierId: ID!,
                  $trackingNumber: String!
                ) {
                  track(
                    carrierId: $carrierId,
                    trackingNumber: $trackingNumber
                  ) {
                    lastEvent {
                      time
                      status {
                        code
                        name
                      }
                      description
                    }
                    events(last: 10) {
                      edges {
                        node {
                          time
                          status {
                            code
                            name
                          }
                          description
                        }
                      }
                    }
                  }
                }
                """.strip(),
                "variables": {
                    "carrierId": del_com_id,
                    "trackingNumber": invoice_num,
                    # "carrierId": "kr.cjlogistics",
                    # "trackingNumber": "1234567890"
                },
            }
        ).json()

        print('배송 추적 : ', track_response['data']['track'])
        result = track_response['data']['track']

        if result is None:
            return JsonResponse({'error': '존재하지 않는 송장번호입니다.'}, status=404)

        # return JsonResponse({'data': result})
        return render(request, 'Delivery/delivery_track_result.html', {'track_data': result})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class DeliveryCompanyGet(View):
    def get(self, request, *args, **kwargs):
        result = DeliveryCompany.objects.all().values(
            'id', 'com_id', 'com_name'
        )
        return JsonResponse({'result': list(result)})



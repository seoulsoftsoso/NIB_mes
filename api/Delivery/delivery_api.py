import requests


def DeliveryList():  # 택배사 조회
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
    return result


def DeliveryTrack():  # 운송장 정보 조회
    track_response = requests.post(
        url="https://apis.tracker.delivery/graphql",
        headers={
            # Instructions for obtaining [YOUR_CLIENT_ID] and [YOUR_CLIENT_SECRET] can be found in the documentation below:
            # See: https://tracker.delivery/docs/authentication
            "Authorization": "TRACKQL-API-KEY 134sr1s6a8aa4e43sr69t0faps:1k7fr3ieqnmltea40313frpk0ei06d6ckonoefjheehl69t4hi0q"
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
                "carrierId": "kr.cjlogistics",
                "trackingNumber": "1234567890"
            },
        }
    ).json()

    print('배송 추적 : ', track_response['data']['track'])
    result = track_response['data']['track']
    return result





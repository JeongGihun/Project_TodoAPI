import requests
import json
# request : HTTP 요청을 위한 라이브러리
# json : json 데이터를 출력하기 위한 라이브러리

BASE_URL = 'http://localhost:5000'

def print_response(title, response):
    print(f"\n{'='*50}")
    print(f"[{title}]")
    print(f"상태 코드: {response.status_code}")
    print(f"응답 내용:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    # response.json() : 응답 data를 딕셔너리화, json.dumps() : 딕셔너리를 json화
    # indent : 들여쓰기 / ensure_ascii=False : 한글 깨지지 않게
    print('='*50)

# 1. CREATE - 할 일 추가
print("\n### 1. CREATE - 할 일 추가 ###")
response = requests.post(f'{BASE_URL}/todos',
    json={
        'title': '알고리즘 문제 풀기',
        'description': '프로그래머스 DP 3문제'
    }
)
# 요청 -> post 메서드로 전달. 아래의 get, delete등도 동일
print_response("할 일 추가", response)

response = requests.post(f'{BASE_URL}/todos',
    json={
        'title': 'Flask 공부',
        'description': 'REST API 만들기'
    }
)
print_response("할 일 추가 2", response)

# 2. READ - 전체 목록 조회
print("\n### 2. READ - 전체 목록 조회 ###")
response = requests.get(f'{BASE_URL}/todos')
print_response("전체 목록", response)

# 3. READ - 특정 할 일 조회
print("\n### 3. READ - 특정 할 일 조회 ###")
response = requests.get(f'{BASE_URL}/todos/1')
print_response("ID 1번 조회", response)

# 4. UPDATE - 할 일 수정
print("\n### 4. UPDATE - 할 일 수정 ###")
response = requests.put(f'{BASE_URL}/todos/1',
    json={
        'title': '알고리즘 문제 풀기 (수정됨)',
        'completed': True
    }
)
print_response("ID 1번 수정", response)

# 수정 후 다시 조회
response = requests.get(f'{BASE_URL}/todos/1')
print_response("수정 후 ID 1번 조회", response)

# 5. DELETE - 할 일 삭제
print("\n### 5. DELETE - 할 일 삭제 ###")
response = requests.delete(f'{BASE_URL}/todos/2')
print_response("ID 2번 삭제", response)

# 삭제 후 전체 목록 조회
response = requests.get(f'{BASE_URL}/todos')
print_response("삭제 후 전체 목록", response)
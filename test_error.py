import requests
import json

BASE_URL = 'http://localhost:5000'


def test_error(title, method, url, data=None):
    """에러 테스트를 위한 함수"""
    print(f"\n{'=' * 60}")
    print(f"[테스트: {title}]")

    # HTTP 메서드에 따라 요청 보내기
    if method == 'POST':
        response = requests.post(url, json=data)
    elif method == 'PUT':
        response = requests.put(url, json=data)
    elif method == 'GET':
        response = requests.get(url)
    elif method == 'DELETE':
        response = requests.delete(url)

    print(f"상태 코드: {response.status_code}")
    print(f"응답:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    # 예상 결과 확인
    if response.status_code >= 400:
        print("✅ 에러 처리 정상 작동")
    else:
        print("⚠️  에러가 발생하지 않음 (문제 있음)")
    print('=' * 60)


print("\n🔍 입력 검증 및 에러 핸들링 테스트 시작\n")

# ========================================
# 400 Bad Request 테스트
# ========================================
print("\n" + "🚨 400 Bad Request 테스트 🚨".center(60))

# 1. 데이터 없이 요청
test_error(
    "1. 빈 데이터로 POST 요청",
    'POST',
    f'{BASE_URL}/todos',
    {}
)

# 2. 제목 없이 요청
test_error(
    "2. 제목 없이 POST 요청 (description만)",
    'POST',
    f'{BASE_URL}/todos',
    {'description': '설명만 있고 제목은 없음'}
)

# 3. 제목이 빈 문자열
test_error(
    "3. 제목이 빈 문자열",
    'POST',
    f'{BASE_URL}/todos',
    {'title': ''}
)

# 4. 제목이 공백만
test_error(
    "4. 제목이 공백만",
    'POST',
    f'{BASE_URL}/todos',
    {'title': '   '}
)

# 5. 제목이 100자 초과
test_error(
    "5. 제목 100자 초과",
    'POST',
    f'{BASE_URL}/todos',
    {'title': 'a' * 101, 'description': '제목이 너무 깁니다'}
)

# ========================================
# UPDATE 관련 에러 테스트
# ========================================
print("\n" + "🚨 UPDATE 에러 테스트 🚨".center(60))

# 먼저 테스트용 할 일 추가
print("\n[준비] 테스트용 할 일 추가...")
response = requests.post(f'{BASE_URL}/todos',
                         json={'title': '에러 테스트용', 'description': '테스트'})
print(f"할 일 추가됨 (ID: {response.json()['data']['id']})")

# 6. 수정 데이터 없음
test_error(
    "6. 수정할 데이터 없이 PUT 요청",
    'PUT',
    f'{BASE_URL}/todos/1',
    {}
)

# 7. 제목을 빈 문자열로 수정
test_error(
    "7. 제목을 빈 문자열로 수정",
    'PUT',
    f'{BASE_URL}/todos/1',
    {'title': ''}
)

# 8. 제목을 100자 초과로 수정
test_error(
    "8. 제목을 100자 초과로 수정",
    'PUT',
    f'{BASE_URL}/todos/1',
    {'title': 'x' * 101}
)

# 9. completed에 문자열 전송
test_error(
    "9. completed에 문자열 전송 (잘못된 타입)",
    'PUT',
    f'{BASE_URL}/todos/1',
    {'completed': "true"}  # 문자열 (잘못됨)
)

# 10. completed에 숫자 전송
test_error(
    "10. completed에 숫자 전송 (잘못된 타입)",
    'PUT',
    f'{BASE_URL}/todos/1',
    {'completed': 1}  # 숫자 (잘못됨)
)

# 11. completed에 문자열 "yes"
test_error(
    "11. completed에 'yes' 전송 (잘못된 값)",
    'PUT',
    f'{BASE_URL}/todos/1',
    {'completed': "yes"}
)

# ========================================
# 404 Not Found 테스트
# ========================================
print("\n" + "🚨 404 Not Found 테스트 🚨".center(60))

# 12. 존재하지 않는 ID 조회
test_error(
    "12. 존재하지 않는 ID 조회 (GET /todos/999)",
    'GET',
    f'{BASE_URL}/todos/999'
)

# 13. 존재하지 않는 ID 수정
test_error(
    "13. 존재하지 않는 ID 수정 (PUT /todos/888)",
    'PUT',
    f'{BASE_URL}/todos/888',
    {'title': '수정 시도'}
)

# 14. 존재하지 않는 ID 삭제
test_error(
    "14. 존재하지 않는 ID 삭제 (DELETE /todos/777)",
    'DELETE',
    f'{BASE_URL}/todos/777'
)

# ========================================
# 추가 엣지 케이스
# ========================================
print("\n" + "🚨 엣지 케이스 테스트 🚨".center(60))

# 15. title이 None
test_error(
    "15. title이 None",
    'POST',
    f'{BASE_URL}/todos',
    {'title': None}
)

# 16. 매우 긴 description (검증 없지만 테스트)
# 문제 없는게 정상임
test_error(
    "16. 매우 긴 description (1000자)",
    'POST',
    f'{BASE_URL}/todos',
    {'title': '테스트', 'description': 'a' * 1000}
)

# 17. 특수문자가 포함된 제목
print(f"\n{'=' * 60}")
print("[테스트: 17. 특수문자 포함 제목 (정상 케이스)]")
response = requests.post(f'{BASE_URL}/todos',
                         json={'title': '!@#$%^&*() 특수문자 테스트'})
print(f"상태 코드: {response.status_code}")
if response.status_code == 201:
    print("✅ 특수문자 처리 정상")
else:
    print("⚠️  예상치 못한 에러")
print('=' * 60)

print("\n✅ 모든 에러 핸들링 테스트 완료!\n")
"""auth 모듈 (B-05): 로그인(JWT), 테이블 QR/세션 토큰, 사용자·테이블 CRUD.

D-25: 이 모듈이 users/tables 테이블과 그 업무 규칙(비밀번호 해시, 토큰 발급·검증,
QR 재발급 시 구토큰 무효화)을 소유한다. 다른 모듈은 app.auth.dependencies의
get_current_role/get_table_id만 의존하고 app.auth.models를 직접 import하지 않는다.
"""

-- 로컬 개발 DB 초기화 스크립트 (PostgreSQL 18, 1회 실행)
-- 실행: psql -U postgres -f scripts/init_local_db.sql

-- 역할 생성 (이미 있으면 skip)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'pos_app') THEN
    CREATE ROLE pos_app WITH LOGIN PASSWORD 'CHANGE_ME';
  END IF;
END
$$;

-- DB 생성 (이미 있으면 skip)
SELECT 'CREATE DATABASE pos_app_dev OWNER pos_app'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'pos_app_dev')\gexec

SELECT 'CREATE DATABASE pos_app_test OWNER pos_app'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'pos_app_test')\gexec

-- 권한 부여
GRANT ALL PRIVILEGES ON DATABASE pos_app_dev TO pos_app;
GRANT ALL PRIVILEGES ON DATABASE pos_app_test TO pos_app;

\echo '완료: pos_app 역할, pos_app_dev, pos_app_test DB 생성됨'

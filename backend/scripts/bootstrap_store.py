"""파일럿 첫 설정 스크립트 (B-10). 여러 번 실행해도 중복이 생기지 않는다.

- owner 계정이 하나도 없을 때만 owner 1명을 만든다. 이미 있으면 아무것도 바꾸지 않는다.
- --tables N: 테이블 1..N을 보장하고 테이블별 QR 접속 주소를 CSV로 쓴다(이미 있는 QR은 그대로).
- --add-user 이름 --role staff|kitchen: 직원/주방 계정을 만든다(이미 있으면 건너뜀).

비밀번호는 환경 변수(POS_OWNER_PASSWORD / POS_USER_PASSWORD)나 입력창으로만 받는다.
코드, 로그, 출력 어디에도 남기지 않는다. 실행: backend 폴더에서
    python scripts/bootstrap_store.py --help
"""
import argparse
import csv
import getpass
import os
import sys
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

MIN_PASSWORD_LEN = 8
ROLES = ("staff", "kitchen")


def read_password(env_name: str, label: str) -> str:
    """환경 변수가 있으면 그것을, 없으면 입력창(화면에 안 보임)에서 두 번 받는다."""
    value = os.environ.get(env_name)
    if not value:
        value = getpass.getpass(f"{label} 비밀번호: ")
        if value != getpass.getpass("한 번 더 입력: "):
            raise SystemExit("비밀번호가 서로 다릅니다. 처음부터 다시 실행해 주세요.")
    if len(value) < MIN_PASSWORD_LEN:
        raise SystemExit(f"비밀번호는 {MIN_PASSWORD_LEN}자 이상이어야 합니다.")
    return value


def qr_url(base_url: str, table) -> str:
    query = urlencode({"table_id": table.id, "qr_token": table.qr_token})
    return f"{base_url.rstrip('/')}/?{query}"


def write_qr_csv(path: str, base_url: str, tables) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig: 엑셀에서 한글이 깨지지 않게
        writer = csv.writer(f)
        writer.writerow(["table_no", "table_id", "url"])
        for t in tables:
            writer.writerow([t.table_no, t.id, qr_url(base_url, t)])


def run(db, args, owner_password=None, user_password=None, out=sys.stderr) -> None:
    from app.auth import service

    if owner_password is not None:
        owner = service.bootstrap_owner(db, username=args.owner_username, password=owner_password)
    else:
        owner = None
    print("사장 계정을 만들었습니다." if owner else "사장 계정이 이미 있어 건너뜁니다.", file=out)

    if args.add_user:
        created = service.ensure_user(db, username=args.add_user, password=user_password, role=args.role)
        print(f"{args.role} 계정 '{args.add_user}'을(를) " + ("만들었습니다." if created else "이미 있어 건너뜁니다."), file=out)

    if args.tables:
        tables = service.ensure_tables(db, count=args.tables)
        write_qr_csv(args.csv_out, args.base_url, tables)
        print(f"테이블 {len(tables)}개의 QR 주소를 {args.csv_out}에 썼습니다. 이 파일은 커밋하지 마세요.", file=out)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="파일럿 첫 설정(사장 계정, 테이블, QR 주소)")
    p.add_argument("--owner-username", default="owner", help="사장 로그인 아이디(기본 owner)")
    p.add_argument("--tables", type=int, default=0, help="만들 테이블 개수 N (1..N)")
    p.add_argument("--base-url", help="손님 화면 주소. 예: https://store.example.com (--tables일 때 필수)")
    p.add_argument("--csv-out", help="QR 주소 CSV 저장 경로 (--tables일 때 필수)")
    p.add_argument("--add-user", help="추가할 직원/주방 계정 아이디")
    p.add_argument("--role", choices=ROLES, help="--add-user의 역할")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.tables < 0:
        raise SystemExit("--tables는 0 이상이어야 합니다.")
    if args.tables and not (args.base_url and args.csv_out):
        raise SystemExit("--tables를 쓰려면 --base-url과 --csv-out이 필요합니다.")
    if bool(args.add_user) != bool(args.role):
        raise SystemExit("--add-user와 --role은 함께 써야 합니다.")

    from app.auth import repository
    from app.db import SessionLocal

    with SessionLocal() as db:
        # 비밀번호는 실제로 계정을 만들 때만 묻는다(이미 있으면 묻지 않고 건너뜀).
        owner_exists = repository.count_users_by_role(db, "owner") > 0
        owner_password = None if owner_exists else read_password("POS_OWNER_PASSWORD", "사장")
        user_exists = bool(args.add_user) and repository.get_user_by_username(db, args.add_user) is not None
        user_password = read_password("POS_USER_PASSWORD", args.add_user) if args.add_user and not user_exists else None
        run(db, args, owner_password, user_password)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

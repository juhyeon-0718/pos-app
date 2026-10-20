"""B-10: 목록 계약 래퍼(users/tables)와 bootstrap_store 멱등성."""
import csv
import importlib.util
import io
from pathlib import Path

from app.auth import repository as auth_repo
from app.auth.models import Table, User
from tests.conftest import auth_header

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "bootstrap_store.py"
_spec = importlib.util.spec_from_file_location("bootstrap_store", _SCRIPT)
bootstrap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bootstrap)

OWNER_PW = "owner-pw-12345"
USER_PW = "staff-pw-12345"


def _run(db, argv, owner_pw=OWNER_PW, user_pw=None):
    out = io.StringIO()
    args = bootstrap.build_parser().parse_args(argv)
    bootstrap.run(db, args, owner_pw, user_pw, out=out)
    return out.getvalue()


def _count(db, model):
    db.expire_all()
    return db.query(model).count()


def test_users_list_has_contract_wrapper(client, db):
    r = client.get("/api/v1/users", headers=auth_header("owner"))
    assert r.status_code == 200, r.text
    body = r.json()
    assert set(body) >= {"items", "next_cursor", "has_more"}
    assert body["next_cursor"] is None and body["has_more"] is False
    assert isinstance(body["items"], list)


def test_tables_list_has_contract_wrapper(client, db):
    auth_repo.create_table(db, table_no=1)
    r = client.get("/api/v1/tables", headers=auth_header("owner"))
    assert r.status_code == 200, r.text
    body = r.json()
    assert set(body) >= {"items", "next_cursor", "has_more"}
    assert body["has_more"] is False and len(body["items"]) == 1


def test_bootstrap_creates_owner_who_can_login(client, db):
    _run(db, [])
    r = client.post("/api/v1/auth/login", json={"username": "owner", "password": OWNER_PW})
    assert r.status_code == 200, r.text
    assert r.json()["role"] == "owner"


def test_bootstrap_rerun_does_not_change_anything(db, tmp_path):
    csv_path = tmp_path / "qr.csv"
    argv = ["--tables", "3", "--base-url", "https://store.example.com", "--csv-out", str(csv_path)]
    _run(db, argv)
    first_hash = db.query(User).one().password_hash
    first_tokens = {t.table_no: t.qr_token for t in db.query(Table).all()}

    out = _run(db, argv, owner_pw="another-pw-98765")
    db.expire_all()
    assert _count(db, User) == 1
    assert _count(db, Table) == 3
    assert db.query(User).one().password_hash == first_hash
    assert {t.table_no: t.qr_token for t in db.query(Table).all()} == first_tokens
    assert "이미 있어 건너뜁니다" in out


def test_bootstrap_skips_when_any_owner_exists(db):
    auth_repo.create_user(db, username="boss", password_hash="x", role="owner")
    out = _run(db, ["--owner-username", "owner2"], owner_pw=None)
    assert _count(db, User) == 1
    assert "이미 있어 건너뜁니다" in out


def test_bootstrap_csv_has_urls_and_no_secrets(db, tmp_path):
    csv_path = tmp_path / "qr.csv"
    out = _run(db, ["--tables", "2", "--base-url", "https://store.example.com/", "--csv-out", str(csv_path)])
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    assert [r["table_no"] for r in rows] == ["1", "2"]
    tables = {t.table_no: t for t in db.query(Table).all()}
    for row in rows:
        t = tables[int(row["table_no"])]
        assert row["url"] == f"https://store.example.com/?table_id={t.id}&qr_token={t.qr_token}"
    text = csv_path.read_text(encoding="utf-8-sig")
    assert OWNER_PW not in text and OWNER_PW not in out


def test_bootstrap_add_user_is_idempotent(client, db):
    argv = ["--add-user", "kitchen1", "--role", "kitchen"]
    _run(db, argv, user_pw=USER_PW)
    h = db.query(User).filter(User.username == "kitchen1").one().password_hash
    out = _run(db, argv, owner_pw=None, user_pw="different-pw-0000")
    db.expire_all()
    assert _count(db, User) == 2  # owner + kitchen1
    assert db.query(User).filter(User.username == "kitchen1").one().password_hash == h
    assert USER_PW not in out
    r = client.post("/api/v1/auth/login", json={"username": "kitchen1", "password": USER_PW})
    assert r.status_code == 200 and r.json()["role"] == "kitchen"

"""B-19: 파일럿 데이터 적재 스크립트. 테스트 데이터는 모두 가짜 값이다(실제 xlsx를 쓰지 않는다)."""
import importlib.util
from pathlib import Path

import pytest

from tests.conftest import auth_header

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "load_pilot_data.py"
_spec = importlib.util.spec_from_file_location("load_pilot_data", _SCRIPT)
loader = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(loader)

PREFIX = "/api/v1"

MENU_ROWS = [
    ("테스트 플레이트", 15000, "main", "Y"),
    ("테스트 안주", 10000, "side", "Y"),
    ("테스트 위스키", 99000, "위스키·증류주", "Y"),
    ("테스트 맥주", 5000, "맥주", "Y"),
    (None, None, None, None),  # 빈 줄은 건너뛴다
]
INGREDIENT_ROWS = [
    ("테스트 닭", "g", 12, 5000, 1000, 2),
    ("테스트 치즈", "g", 30, 1500, 300, 2),
    ("테스트 병맥주", "병", 1000, 30, 12, 2),
]


class _Api:
    """TestClient를 /api/v1 아래 상대 경로로 쓰게 하는 얇은 어댑터(httpx.Client 호환 부분만)."""

    def __init__(self, client):
        self._c = client

    def get(self, path, **kw):
        return self._c.get(PREFIX + path, **kw)

    def post(self, path, **kw):
        return self._c.post(PREFIX + path, **kw)

    def patch(self, path, **kw):
        return self._c.patch(PREFIX + path, **kw)


@pytest.fixture
def api(client):
    return _Api(client)


@pytest.fixture
def token():
    return auth_header("owner")["Authorization"].split(" ", 1)[1]


def _run(api, token, **kw):
    menus = loader.parse_menu_rows(MENU_ROWS)
    ingredients = loader.parse_ingredient_rows(INGREDIENT_ROWS)
    return loader.run(api, token, menus, ingredients, **kw)


def _menus(client):
    return client.get(f"{PREFIX}/menus", headers=auth_header("owner")).json()["items"]


def _ingredients(client):
    return client.get(f"{PREFIX}/ingredients", headers=auth_header("owner")).json()["items"]


def test_parse_marks_non_main_side_as_inactive():
    menus = {m.name: m for m in loader.parse_menu_rows(MENU_ROWS)}
    assert len(menus) == 4
    assert menus["테스트 플레이트"].is_active and menus["테스트 안주"].is_active
    assert not menus["테스트 위스키"].is_active and not menus["테스트 맥주"].is_active


def test_parse_rounds_to_server_precision():
    row = loader.parse_ingredient_rows([("x", "병", 1403.333333333333, 30, 12, 2)])[0]
    assert row.unit_price == 1403.33


def test_parse_rejects_bad_rows():
    with pytest.raises(loader.LoadError):
        loader.parse_menu_rows([("a", 1000, "main", "Y"), ("a", 2000, "main", "Y")])  # 이름 중복
    with pytest.raises(loader.LoadError):
        loader.parse_menu_rows([("a", "천원", "main", "Y")])  # 가격이 숫자가 아님
    with pytest.raises(loader.LoadError):
        loader.parse_menu_rows([("a", 1000, "main", "?")])  # Y/N 아님
    with pytest.raises(loader.LoadError):
        loader.parse_ingredient_rows([("x", "", 1, 1, 1, 1)])  # 단위 없음
    with pytest.raises(loader.LoadError):
        loader.parse_ingredient_rows([("x", "g", 1, -5, 1, 1)])  # 음수 재고


def test_dry_run_writes_nothing(client, api, token):
    report = _run(api, token, dry_run=True)
    assert report.created["menus"] == 4 and report.created["ingredients"] == 3
    assert _menus(client) == [] and _ingredients(client) == []


def test_load_creates_everything_and_second_run_creates_nothing(client, api, token):
    first = _run(api, token)
    assert first.created == {"menus": 4, "ingredients": 3, "stock_movements": 3}

    menus = {m["name"]: m for m in _menus(client)}
    assert len(menus) == 4
    assert menus["테스트 플레이트"]["is_active"] is True
    assert menus["테스트 위스키"]["is_active"] is False  # 주류는 일시품절로 들어간다
    stock = {i["name"]: i for i in _ingredients(client)}
    assert len(stock) == 3
    assert stock["테스트 병맥주"]["current_stock"] == 30
    assert stock["테스트 병맥주"]["safety_stock"] == 12 and stock["테스트 병맥주"]["lead_time_days"] == 2

    second = _run(api, token)
    assert second.created == {"menus": 0, "ingredients": 0, "stock_movements": 0}
    assert second.updated == {"menus": 0, "ingredients": 0}
    assert len(_menus(client)) == 4 and len(_ingredients(client)) == 3
    assert {i["name"]: i["current_stock"] for i in _ingredients(client)}["테스트 병맥주"] == 30  # 재고 이중 입고 없음


def test_rerun_updates_changed_price_but_create_only_leaves_it(client, api, token):
    _run(api, token)
    changed = [r if r[0] != "테스트 안주" else ("테스트 안주", 12000, "side", "Y") for r in MENU_ROWS]
    menus = loader.parse_menu_rows(changed)
    ingredients = loader.parse_ingredient_rows(INGREDIENT_ROWS)

    kept = loader.run(api, token, menus, ingredients, create_only=True)
    assert kept.updated == {"menus": 0, "ingredients": 0}
    assert {m["name"]: m["price"] for m in _menus(client)}["테스트 안주"] == 10000

    fixed = loader.run(api, token, menus, ingredients)
    assert fixed.updated["menus"] == 1 and fixed.created["menus"] == 0
    assert {m["name"]: m["price"] for m in _menus(client)}["테스트 안주"] == 12000
    assert len(_menus(client)) == 4


def test_http_error_becomes_load_error(client, api):
    with pytest.raises(loader.LoadError):
        loader.run(api, "not-a-token", loader.parse_menu_rows(MENU_ROWS), [], dry_run=True)


def test_read_workbook_from_xlsx(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "메뉴"
    ws.append(["이름", "가격", "종류", "판매"])
    for row in MENU_ROWS[:2]:
        ws.append(row)
    ws2 = wb.create_sheet("식재료")
    ws2.append(["이름", "단위", "단가", "현재고", "안전재고", "리드타임"])
    ws2.append(INGREDIENT_ROWS[0])
    path = tmp_path / "fake.xlsx"
    wb.save(path)
    menus, ingredients = loader.read_workbook(path)
    assert [m.name for m in menus] == ["테스트 플레이트", "테스트 안주"]
    assert [i.name for i in ingredients] == ["테스트 닭"]
    with pytest.raises(loader.LoadError):
        loader.read_workbook(tmp_path / "missing.xlsx")

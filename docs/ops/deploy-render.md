# Render 배포 절차 (B-11, D-36)

정주현 님이 처음부터 끝까지 그대로 따라 하는 문서입니다. 저장소 루트의 `render.yaml`(Blueprint) 하나로 서비스 3개를 한 번에 만듭니다.

> **비밀값 경고**: `DATABASE_URL`, `JWT_SECRET`, 비밀번호, QR 주소 파일(`table-qr-urls.csv`)은 **Slack·채팅·git·스크린샷에 붙이지 마세요.** 로그를 개발팀에 보낼 때도 접속 문자열(`postgresql://사용자:비밀번호@...`)이 보이면 그 부분을 가린 뒤 보내세요.

## 만들어지는 것

- `pos-app-api`: 백엔드 Web Service. Starter 플랜(월 $7), 싱가포르, `backend/` 폴더. 배포 직전에 `alembic upgrade head`가 자동 실행됩니다.
- `pos-app-db`: Postgres 18, `basic-256mb` 플랜(월 $6) + 저장공간 1GB(월 약 $0.30). 싱가포르.
- `pos-app-web`: 프론트 Static Site. `frontend/` 폴더, 빌드 결과 `dist`. 요금 없음(정적 사이트).
- 예상 비용: 월 약 $13~14. 모든 요금은 Render 요금 페이지 기준이며 바뀔 수 있습니다.
- 주소는 하나로 묶입니다. 프론트 주소의 `/api/*`는 백엔드로 넘어가고, 나머지는 `/index.html`입니다. 그래서 손님·직원·사장 모두 프론트 주소 하나만 씁니다.

## 1단계. Blueprint 연결

1. [dashboard.render.com/blueprints](https://dashboard.render.com/blueprints)에서 **New Blueprint Instance**를 누릅니다.
2. 저장소 `pos-app`을 고르고 브랜치는 `main`을 고릅니다. (저장소가 안 보이면 Render GitHub App에 `juhyeon-0718/pos-app` 읽기 권한을 주세요.)
3. Blueprint 이름을 넣고(예: `pos-app`), 화면에 나오는 **서비스 3개와 plan**을 확인합니다.
   - `pos-app-api` — Web Service — Starter
   - `pos-app-web` — Static Site
   - `pos-app-db` — PostgreSQL — Basic 256MB (18)
4. 다른 값을 입력하라는 칸이 나오지 않는 것이 정상입니다. `JWT_SECRET`은 Render가 생성하고 `DATABASE_URL`은 DB에서 자동 연결됩니다.
5. **Apply**를 누릅니다.

이렇게 나오면 성공: 세 서비스가 모두 **Live**(DB는 **Available**)가 됩니다. 백엔드 첫 배포는 몇 분 걸립니다.

실패 시 볼 화면: 서비스 → **Logs**. 마이그레이션이 실패하면 **Events** 탭에 `Pre-deploy command failed`가 표시되고 Logs에 오류 줄이 나옵니다.

## 2단계. 백엔드 주소 확인 (rewrite 주소 맞추기)

프론트의 `/api/*`는 `render.yaml`에 적힌 `https://pos-app-api.onrender.com`으로 넘어갑니다. 이름이 다른 사람과 겹치면 Render가 주소 끝에 글자를 붙입니다.

1. `pos-app-api` 서비스 화면 왼쪽 위의 주소(`https://....onrender.com`)를 확인합니다.
2. **정확히 `https://pos-app-api.onrender.com`이면** 이 단계는 끝입니다.
3. 다르면(예: `https://pos-app-api-x1y2.onrender.com`): `pos-app-web` → **Redirects/Rewrites**에서 `/api/*` 규칙의 Destination을 `https://<실제 백엔드 주소>/api/*`로 고치고 저장합니다. 그 뒤 개발팀에 알려 주세요(`render.yaml`도 같은 값으로 고쳐야 다음 배포에서 되돌아가지 않습니다).

## 3단계. 배포 확인

`pos-app-web`의 주소(이하 `<프론트주소>`)를 확인하고 PowerShell에서 실행합니다.

```
curl.exe https://<프론트주소>/api/v1/health
```

이렇게 나오면 성공:

```
{"status":"ok"}
```

브라우저에서 `https://<프론트주소>/`도 열어 화면이 나오는지 봅니다.

| 증상 | 볼 곳 |
|---|---|
| `{"status":"ok"}` 대신 화면(HTML)이 나옴 | 2단계 rewrite 순서·주소. `pos-app-web` → Redirects/Rewrites에서 `/api/*`가 `/*`보다 위에 있는지 |
| 502/503 | `pos-app-api` → **Logs**. `JWT_SECRET 환경변수가 필요합니다` 또는 `DATABASE_URL 환경변수가 필요합니다`가 보이면 **Environment** 탭에서 두 변수가 있는지 확인 |
| 처음 1~2분 응답 없음 | 첫 배포 직후는 정상. 3분이 넘으면 `pos-app-api` → **Logs** |
| 배포 자체가 `Pre-deploy command failed` | `pos-app-api` → **Logs**의 마지막 오류 줄 (마이그레이션 오류) |

## 4단계. 내 PC에서 운영 DB에 연결할 준비

계정·테이블 만들기(5단계)는 내 PC에서 `scripts/bootstrap_store.py`를 실행하며, 운영 DB에 직접 연결합니다.

1. Render에서 `pos-app-db` → **Connect** → **External** 탭의 **External Database URL**을 복사합니다. (화면에서 복사 버튼만 쓰세요. 채팅에 붙이지 않습니다.)
2. PowerShell을 열고 아래를 **한 줄씩** 실행합니다. 따옴표 안에 복사한 주소를 붙여 넣습니다.

```
cd C:\juehyeon\pos-app\main\backend
$env:ENV = "prod"
$env:DATABASE_URL = "여기에 External Database URL 붙여넣기"
$env:JWT_SECRET = "이-PC에서만-쓰는-임시-문자열-32자-이상-아무거나"
```

- `JWT_SECRET`은 이 PC의 스크립트가 시작되기 위해서만 필요한 임시 값입니다. 서버의 `JWT_SECRET`과 같을 필요가 없고, 같게 만들지도 마세요.
- PowerShell 창을 닫으면 이 값들은 사라집니다. 작업이 끝나면 창을 닫습니다.
- 가상환경(venv)이 있으면 먼저 켭니다.

연결 확인:

```
python -m alembic current
```

이렇게 나오면 성공: 마지막 줄 끝에 `(head)`가 붙은 번호(예: `a3d9b12e5c40 (head)`). 1단계의 배포 전 명령이 이미 마이그레이션을 끝낸 상태입니다. (이후 작업으로 번호는 바뀔 수 있습니다.)

실패 시: `connection refused`/시간 초과면 `pos-app-db` → **Info**에서 상태가 Available인지, **Networking**의 허용 IP가 막혀 있지 않은지 확인합니다.

## 5단계. 사장 계정과 테이블 QR 만들기 (B-10)

자세한 설명과 옵션은 [pilot-setup.md](pilot-setup.md) 2~3단계를 따릅니다. 4단계의 PowerShell 창에서 이어서 실행하되 **`--base-url`에 Render 프론트 주소를 씁니다.**

```
python scripts/bootstrap_store.py --tables 10 --base-url https://<프론트주소> --csv-out C:\Users\본인이름\Desktop\table-qr-urls.csv
```

사장 비밀번호(8자 이상)를 두 번 입력합니다(입력해도 화면에 안 보이는 것이 정상).

이렇게 나오면 성공:

```
사장 계정을 만들었습니다.
테이블 10개의 QR 주소를 C:\Users\본인이름\Desktop\table-qr-urls.csv에 썼습니다. 이 파일은 커밋하지 마세요.
```

직원·주방 계정:

```
python scripts/bootstrap_store.py --add-user staff1 --role staff
python scripts/bootstrap_store.py --add-user kitchen1 --role kitchen
```

이렇게 나오면 성공: `staff 계정 'staff1'을(를) 만들었습니다.` / `kitchen 계정 'kitchen1'을(를) 만들었습니다.`

확인: 브라우저에서 `https://<프론트주소>/owner`로 가서 `owner`와 방금 정한 비밀번호로 로그인합니다. 사장 화면이 열리면 성공입니다.

실패 시:
- 스크립트에서 연결 오류: 4단계의 `DATABASE_URL`이 맞는지 확인합니다(주소를 화면에 다시 출력하지 마세요).
- 로그인이 안 됨: `pos-app-api` → **Logs**에서 `POST /api/v1/auth/login` 줄의 상태 코드를 확인합니다(401이면 아이디·비밀번호 문제).
- 다시 실행해도 안전합니다. 이미 있는 계정·테이블은 `이미 있어 건너뜁니다.`로 넘어갑니다.

QR 주소 파일은 비밀 정보와 같으니 QR 인쇄가 끝나면 지웁니다. 자체 도메인으로 바꾸면 QR을 다시 인쇄해야 합니다(D-36).

## 6단계. 메뉴 32개·식재료 38개 입력 (B-19) — B-19(PR #37) 머지 후

> **이 단계는 B-19(PR #37)가 `main`에 머지된 뒤에 합니다.** 머지 후 `main`이 Render에 자동 배포되고 스크립트 파일이 PC의 `main` 폴더에 들어옵니다. 머지 전에는 하지 마세요. 아래 명령은 PR #37 기준이며 머지 때 바뀌면 이 문서도 같이 고칩니다.

준비: 입력 파일 `pilot-store-data.xlsx`를 저장소 밖 개인 폴더에 둡니다. 이 단계는 DB에 직접 붙지 않고 **Render 주소의 공개 API**로 입력하므로 4단계의 `DATABASE_URL`은 필요 없습니다. 새 PowerShell 창을 쓰는 것을 권합니다.

```
cd C:\juehyeon\pos-app\main\backend
git -C .. pull --ff-only
```

먼저 읽기만 하는 모의 실행(`--dry-run`)으로 무엇이 들어갈지 봅니다. 사장 비밀번호를 물어봅니다.

```
python scripts/load_pilot_data.py --base-url https://<프론트주소> --xlsx C:\Users\본인이름\Desktop\pilot-store-data.xlsx --dry-run
```

이렇게 나오면 성공: 메뉴 32개, 식재료 38개를 만들 예정이라는 요약이 나오고 오류가 없습니다. (정확한 문구는 스크립트 출력을 따르며, 개수가 다르면 입력 파일을 확인합니다.) 주류 등 `main`/`side`가 아닌 메뉴는 일시품절로 들어갑니다.

문제 없으면 `--dry-run`을 빼고 같은 명령을 실행합니다.

```
python scripts/load_pilot_data.py --base-url https://<프론트주소> --xlsx C:\Users\본인이름\Desktop\pilot-store-data.xlsx
```

확인: 사장 화면(`/owner`)의 메뉴·재고 화면에서 메뉴 32개, 식재료 38개가 보이는지 확인합니다. 여러 번 실행해도 중복이 생기지 않습니다.

실패 시 볼 화면: 스크립트의 `오류:` 줄(몇 번째 행이 문제인지 나옴). 서버 쪽 오류면 `pos-app-api` → **Logs**.

## 7단계. 이후 배포

- `main`에 머지되면 Render가 자동 배포합니다. 배포 직전에 마이그레이션이 자동 실행됩니다.
- 마이그레이션이 실패하면 새 버전은 배포되지 않고 이전 버전이 계속 돌아갑니다(`Events`에서 확인).
- DB는 유료 플랜이라 자동 백업이 켜져 있습니다(`pos-app-db` → **Recovery**).
- 무료 플랜이 아니므로 서비스가 잠들지 않습니다.

## 근거 (Render 공식 문서)

- Blueprint 필드(`preDeployCommand`, `generateValue`, `fromDatabase`, `routes`, `postgresMajorVersion`): <https://render.com/docs/blueprint-spec>
- 플랜 이름·구 이름 매핑(`starter`=`0.5c-512mb`, `basic-256mb`=`0.1c-256mb`): <https://render.com/docs/compute-plans>
- 정적 사이트 rewrite 규칙: <https://render.com/docs/redirects-rewrites>
- Postgres 생성·버전 13~18·저장공간·내부/외부 URL: <https://render.com/docs/postgresql-creating-connecting>
- 배포 전 명령: <https://render.com/docs/deploys>
- 요금: <https://render.com/pricing>

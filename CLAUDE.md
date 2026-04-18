# CLAUDE.md — Algorithms 레포지토리 컨텍스트

## 프로젝트 목적

BaekjoonHub 크롬 익스텐션이 알고리즘 풀이를 이 레포에 자동 커밋할 때마다,
Notion DB에 미등록된 문제를 감지해 정해진 템플릿으로 페이지를 자동 생성한다.

```
BaekjoonHub 커밋 push (main)
        ↓
GitHub Actions (notion-sync.yml)
        ↓
Python 동기화 스크립트 (scripts/)
        ↓
Notion DB 페이지 자동 생성
```

---

## 레포지토리 구조

```
Algorithms/
├── 백준/C++17/{번호}. {제목} ({레벨})/
│   ├── {제목}.cc
│   └── README.md
├── SWEA/C++/{번호}. {제목} (Unrated)/
│   ├── {제목}.cpp
│   └── README.md
├── scripts/
│   ├── notion_sync.py      # 메인 진입점
│   ├── repo_scanner.py     # 레포 디렉토리 스캔
│   ├── readme_parser.py    # README.md 파싱
│   ├── notion_api.py       # Notion API 래퍼
│   ├── tag_mapper.py       # 분류 → 태그 변환
│   ├── page_builder.py     # Notion 블록 구조 생성
│   └── requirements.txt
├── .github/workflows/
│   └── notion-sync.yml     # main push마다 트리거
├── .env                    # 로컬 전용 (gitignore됨)
└── CLAUDE.md               # 이 파일
```

---

## 환경 변수

| 변수명 | 설명 |
|---|---|
| `NOTION_TOKEN` | Notion Integration 토큰 (`ntn_...`) |
| `NOTION_DATABASE_ID` | Notion DB ID (하이픈 없는 32자) |

- **로컬**: `.env` 파일에 저장 (`NOTION_DB_ID`도 동일하게 인식)
- **GitHub Actions**: Repository Secrets에 `NOTION_TOKEN`, `NOTION_DATABASE_ID` 등록

---

## 로컬 실행

```bash
# 의존성 설치
pip install -r scripts/requirements.txt

# 드라이런 (Notion 변경 없이 감지만)
set -a && source .env && set +a
python scripts/notion_sync.py --dry-run

# 실제 등록
python scripts/notion_sync.py
```

---

## Notion DB 정보

- **DB ID**: `33e10fe5c97b80e89babe7e735c40bb9`
- **URL**: https://www.notion.so/33e10fe5c97b80e89babe7e735c40bb9

### 프로퍼티 매핑

| Notion 프로퍼티 | 타입 | 스크립트 소스 |
|---|---|---|
| 제목 | title | `[{번호}] {제목}` 포맷 |
| 문제 사이트 | select | 경로 (`백준/` → `백준`, `SWEA/` → `SWEA`) |
| 문제 레벨 | select | 폴더명 괄호 내 레벨 |
| 태그 | multi_select | README 분류 (TAG_MAP 변환 후 미매핑은 원문 그대로) |
| 사용 언어 | select | 코드 파일 확장자 (`.cc`/`.cpp` → `C++`) |
| 문제 주소 | url | README 문제 링크 |
| 포스팅 상태 | status | 항상 `시작 전` |
| 포스팅 수준 | select | 항상 `코드만` |

---

## Notion 페이지 템플릿 구조

```
{#분류1 #분류2 ...}          ← 없음 (태그는 DB 프로퍼티에만)

## 문제
- [문제 URL]
{문제 설명 plain text}
### 입력
### 출력
---
### 문제 조건                 ← scaffolding (사용자 작성)
- 목표: (비워둠)
- 입력 상태: (비워둠)
- 핵심 조건: (비워둠)
---
## 풀이
### 핵심 알고리즘
`{대표 분류}`                ← inline code
- 시간 복잡도: O(?)
### 핵심 아이디어
(비워둠)
---
### 성능
- **메모리 :** {X} KB       ← yellow_background 불릿
- **시간 :** {Y} ms
### 코드 ({언어})
```code```
---
## 소감
### 배운 점
### 다음에 기억할 것
```

---

## 모듈별 책임

### `repo_scanner.py`
- `백준/C++17/`, `SWEA/C++/` 하위 탐색
- 폴더명 파싱 → `ProblemEntry(number, title, level, site, folder_path, readme_path, code_path)`
- `scan_repo(repo_root) → list[ProblemEntry]`

### `readme_parser.py`
- `### 분류`, `### 성능 요약`, `### 제출 일자`, `### 문제 설명` 등 섹션 추출
- HTML 태그 제거 시 `<p>`/`<div>`만 줄바꿈 처리, 인라인 태그(`<strong>`, `<sub>` 등)는 separator="" 적용
  - **주의**: `get_text(separator="\n")` 사용 금지 — 인라인 태그 사이에 불필요한 줄바꿈 삽입됨
- `parse_readme(path) → ReadmeData`

### `tag_mapper.py`
- `TAG_MAP`에 정의된 한국어/영문 분류를 Notion 태그명으로 변환
- **매핑 없는 분류는 원문 그대로 태그에 추가** (제약 없음)
- 영문 분류 직접 매핑 포함: `BFS`, `DFS`, `DP`
- 오타 변형 처리: `백트레킹` → `백트래킹`

### `notion_api.py`
- **파일명 주의**: `notion_client.py`로 명명하면 pip 패키지 `notion-client`와 import 충돌 발생
- `get_registered_numbers()`: DB 전체 조회, `[숫자]` 패턴으로 문제번호 Set 반환
- `create_notion_page(properties, children)`: 100블록 단위 배치 생성
- Rate limit(429) 시 60초 대기 후 최대 3회 재시도

### `page_builder.py`
- `build_children(readme, code, folder_path, lang) → list[dict]`
- Notion 블록 객체 리스트 반환 (markdown 문자열 아님)
- 코드 블록은 2000자 단위로 분할 (Notion API 제한)
- 성능 블록: callout 대신 `yellow_background` 색상 bullet 사용 (callout은 아이콘 제거 불가)

### `notion_sync.py`
- `sys.path.insert(0, scripts_dir)` 로 스크립트 직접 실행 시 sibling import 처리
- 중복 감지: Notion 제목의 `[숫자]` 패턴 vs 레포 폴더명 앞 숫자 비교
- `--dry-run`: NOTION_TOKEN 있으면 Notion 조회 후 미등록 목록만 출력, 없으면 전체 출력

---

## GitHub Actions

- **파일**: `.github/workflows/notion-sync.yml`
- **트리거**: `main` 브랜치 모든 push
- **Secrets 필요**: `NOTION_TOKEN`, `NOTION_DATABASE_ID`
- Python 3.11, `pip install -r scripts/requirements.txt` 후 `python scripts/notion_sync.py` 실행

---

## 알려진 설계 결정 및 주의사항

1. **`notion_api.py` 네이밍**: pip 패키지 `notion-client`가 `notion_client`로 임포트되므로 충돌 방지를 위해 `notion_api.py`로 명명
2. **성능 블록 callout 미사용**: Notion API는 callout 블록 생성 시 아이콘을 항상 자동 추가하며 제거 불가. `yellow_background` bullet으로 대체
3. **HTML 파싱**: BeautifulSoup `get_text(separator="\n")`은 `<strong>`, `<sub>` 같은 인라인 태그 사이에도 줄바꿈 삽입 → `<p>/<div>`만 줄바꿈 처리 후 `separator=""` 사용
4. **태그 자유도**: 초기에는 TAG_MAP에 있는 분류만 태그로 등록했으나, 현재는 미매핑 분류도 원문 그대로 등록 (사용자 요청)
5. **SWEA 분류**: 영문(`BFS`, `DFS`) 및 오타(`백트레킹`) 변형 처리 TAG_MAP에 포함

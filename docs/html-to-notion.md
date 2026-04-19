# 문제 설명 HTML → Notion 블록 변환 로직

BaekjoonHub 크롬 익스텐션이 커밋하는 README.md의 `### 문제 설명` 섹션은  
백준 문제 페이지의 HTML을 그대로 담고 있다.  
`page_builder.py`의 `html_to_notion_blocks()` 함수가 이 HTML을 Notion API 블록 배열로 변환한다.

---

## 1. 입력 구조 (BaekjoonHub README HTML)

백준 문제 설명은 다음 HTML 요소들로 구성된다.

| HTML 요소 | 용도 |
|---|---|
| `<p>` | 일반 설명 문단 |
| `<pre>` | 격자·예제 입출력 (등폭 표현 필요) |
| `<img>` | 문제 다이어그램·그림 |
| `<table>` | CCTV 종류 그림 테이블, 방향 예제 테이블, 입출력 표 등 |
| `<ul>` / `<ol>` | 조건·규칙 목록 |

---

## 2. 변환 규칙 (요소별)

### 2-1. `<p>` → paragraph 블록

```
<p>스타트링크의 사무실은 N×M 크기의 직사각형이다.</p>
```
↓
```json
{ "type": "paragraph", "paragraph": { "rich_text": [{ "text": { "content": "스타트링크의 사무실은 N×M 크기의 직사각형이다." } }] } }
```

---

### 2-2. `<pre>` → code 블록 (language: plain text)

격자나 예제처럼 공백 정렬이 의미 있는 내용은 등폭 코드 블록으로 보존한다.

```
<pre>0 0 0 0 0 0
0 0 1 0 6 0
0 0 0 0 0 0</pre>
```
↓
```json
{ "type": "code", "code": { "rich_text": [{ "text": { "content": "0 0 0 0 0 0\n0 0 1 0 6 0\n0 0 0 0 0 0" } }], "language": "plain text" } }
```

---

### 2-3. `<img>` → image 블록 (외부 URL)

```
<img src="https://onlinejudgeimages.s3.../1.png">
```
↓
```json
{ "type": "image", "image": { "type": "external", "external": { "url": "https://onlinejudgeimages.s3.../1.png" } } }
```

---

### 2-4. `<ul>` / `<ol>` → bulleted_list_item 블록

```html
<ul>
  <li>CCTV는 벽을 통과할 수 없다.</li>
  <li>CCTV는 CCTV를 통과할 수 있다.</li>
</ul>
```
↓
```json
{ "type": "bulleted_list_item", "bulleted_list_item": { "rich_text": [{ "text": { "content": "CCTV는 벽을 통과할 수 없다." } }] } }
{ "type": "bulleted_list_item", "bulleted_list_item": { "rich_text": [{ "text": { "content": "CCTV는 CCTV를 통과할 수 있다." } }] } }
```

---

### 2-5. `<table>` — 내용에 따라 3가지 경로

#### 경로 A: `<img>` 또는 `<pre>` 포함 → **column_list 블록**

Notion의 table 셀은 rich text만 허용하므로 이미지·코드 블록을 셀 안에 넣을 수 없다.  
대신 `column_list` → `column` 구조를 사용해 열(column) 레이아웃을 재현한다.

**변환 방식: 행 기반 → 열 기반 전치(transpose)**

원본 HTML 테이블은 행(row) 우선으로 구성되지만,  
`column_list`는 열(column) 우선이므로 전치가 필요하다.

```
HTML 테이블 (행 우선)         Notion column_list (열 우선)

행1: [img1] [img2] [img3]      열1: img1 → "1번"
행2: ["1번"]["2번"]["3번"]  →   열2: img2 → "2번"
                               열3: img3 → "3번"
```

각 열(column)의 자식 블록은 `_cell_to_blocks()`가 결정한다:

| 셀 내용 | 생성 블록 |
|---|---|
| `<img>` + 텍스트 | image 블록 + paragraph (캡션) |
| `<pre>` + 텍스트 | code 블록 (plain text) + paragraph (캡션) |
| 텍스트만 | paragraph |

**예시 — 감시(15683) CCTV 종류 테이블:**

```
HTML                           Notion
┌──────────────────────┐       column_list
│ <img 1.png> │ <img 2.png> │  ├─ column: [image(1.png), paragraph("1번")]
│ "1번"       │ "2번"       │  ├─ column: [image(2.png), paragraph("2번")]
└──────────────────────┘       └─ ...
```

**예시 — 감시(15683) 방향 예제 테이블:**

```
HTML                           Notion
┌──────────────────────┐       column_list
│ <pre>grid→</pre> │ ...│       ├─ column: [code("0 0 1 # ..."), paragraph("→")]
│ "→"              │ ...│       ├─ column: [code("# # 1 0 ..."), paragraph("←")]
└──────────────────────┘       └─ ...
```

---

#### 경로 B: 텍스트만 → **Notion table 블록**

이미지·코드가 없는 순수 텍스트 표는 Notion 네이티브 테이블로 변환한다.

```html
<table>
  <tr><th>입력</th><th>출력</th></tr>
  <tr><td>5</td><td>3</td></tr>
</table>
```
↓
```json
{
  "type": "table",
  "table": {
    "table_width": 2,
    "has_column_header": false,
    "has_row_header": false,
    "children": [
      { "type": "table_row", "table_row": { "cells": [[{"text":{"content":"입력"}}], [{"text":{"content":"출력"}}]] } },
      { "type": "table_row", "table_row": { "cells": [[{"text":{"content":"5"}}], [{"text":{"content":"3"}}]] } }
    ]
  }
}
```

---

## 3. 전체 처리 흐름

```
README.md
  └─ ### 문제 설명 섹션 (raw HTML)
        │
        │  readme_parser.py
        │  parse_readme() → ReadmeData.description_html (raw HTML 보존)
        │                 → ReadmeData.description      (plain text, AI 프롬프트용)
        │
        ▼
  html_to_notion_blocks(description_html)
        │
        │  BeautifulSoup로 HTML 파싱
        │  최상위 자식 노드를 순서대로 process()
        │
        ├─ NavigableString → paragraph (공백 아닐 때)
        ├─ <p>             → paragraph
        ├─ <pre>           → code (plain text)
        ├─ <img>           → image
        ├─ <ul>/<ol>       → bulleted_list_item × N
        ├─ <table>         → has_media? column_list : table
        ├─ <h1>~<h6>       → heading_3
        └─ 기타 블록       → paragraph (텍스트 추출)
        │
        ▼
  Notion 블록 배열 → notion_api.py → Notion 페이지
```

---

## 4. 설계 결정 및 제약

| 항목 | 결정 | 이유 |
|---|---|---|
| `description`과 `description_html` 분리 | plain text는 AI 프롬프트에, HTML은 Notion에 사용 | AI는 마크업 없는 텍스트가 더 정확 |
| `<table>` with media → `column_list` | Notion table 셀은 rich text만 허용 | 이미지·코드 블록을 셀 안에 못 넣는 Notion API 제약 |
| `children`을 타입별 객체 안에 배치 | `table.children`, `column_list.children`, `column.children` | Notion API 요구사항 (최상위 `"children"` 키 불허) |
| `<pre>` → `"plain text"` 언어 코드 블록 | 구문 강조 불필요, 공백 정렬만 보존 | 격자·예제는 등폭 표현이 목적 |
| 텍스트 2000자 청크 | Notion rich_text 단일 항목 최대 2000자 제한 | API 제한 |

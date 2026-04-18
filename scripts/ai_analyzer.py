"""
Google Gemini 1.5 Flash 모델을 이용한 알고리즘 문제 자동 분석 모듈
google-generativeai SDK 사용 (GEMINI_API_KEY 필요)

Required env var:
    GEMINI_API_KEY    Google AI Studio API 키
"""

import json
import os
import re
from dataclasses import dataclass, field

MODEL_ID = "gemini-3-flash-preview"

_model = None


# -----------------------------------------------------------------------
# 출력 스키마
# -----------------------------------------------------------------------

@dataclass
class AnalysisStep:
    제목: str = ""
    설명: str = ""
    코드: str = ""


@dataclass
class AnalysisResult:
    목표: str = ""
    입력_상태: str = ""
    핵심_조건: str = ""
    시간_복잡도: str = "O(?)"
    핵심_아이디어_개요: str = ""
    핵심_아이디어_단계: list = field(default_factory=list)   # list[AnalysisStep]


# -----------------------------------------------------------------------
# 시스템 프롬프트
# -----------------------------------------------------------------------

SYSTEM_PROMPT = """\
당신은 알고리즘 풀이 분석 전문가입니다.
주어진 문제 설명과 C++ 코드를 분석하여 반드시 JSON 형식으로만 응답하세요.
마크다운 코드블록(```) 없이 순수 JSON 텍스트만 출력하세요.

[설명 작성 규칙]
- 각 단계의 설명은 "무엇을 한다"가 아니라 "왜 이렇게 하는가"를 중심으로 작성하세요.
- 이전 단계와의 연결(이 단계의 결과가 다음 단계에서 어떻게 쓰이는지)을 반드시 포함하세요.
- 코드에 dead code, 논리 오류, 특이한 상수(예: 999999) 등 주목할 만한 점이 있으면 설명에 포함하세요.
- 코드는 제공된 원본에서 그대로 발췌하고, 절대 요약하거나 "..."으로 생략하지 마세요.

[출력 형식]
{
  "목표": "문제가 최종적으로 구하는 것 (한 문장)",
  "입력_상태": "입력 데이터의 크기·구조·제약 (한 문장)",
  "핵심_조건": "풀이에서 반드시 처리해야 할 규칙 (한두 문장)",
  "시간_복잡도": "O(표기법) — 최악의 경우 구체적인 수치 포함",
  "핵심_아이디어_개요": "전체 알고리즘 흐름 요약 (2~3문장)",
  "핵심_아이디어_단계": [
    {
      "제목": "① 단계명",
      "설명": "왜 이 방식을 선택했는지 + 다음 단계와의 연결 (2~3문장)",
      "코드": "이 단계에 해당하는 핵심 코드 발췌 (원본 그대로, 생략 없이)"
    },
    { "제목": "② 단계명", "설명": "...", "코드": "..." },
    { "제목": "③ 단계명", "설명": "...", "코드": "..." }
  ]
}

[예시 — Tarjan's Offline LCA]
{
  "목표": "N개의 정점 트리에서 M개의 쿼리에 대해 두 노드의 최소 공통 조상(LCA)을 구한다.",
  "입력_상태": "N(≤100,000)개의 정점 트리와 M(≤100,000)개의 LCA 쿼리가 주어진다.",
  "핵심_조건": "모든 쿼리를 미리 수집한 뒤 DFS 단 한 번으로 처리해야 효율적이며, 자식 탐색이 완전히 끝난 뒤 Union-Find로 병합해야 한다.",
  "시간_복잡도": "O((N + M) · α(N))",
  "핵심_아이디어_개요": "Tarjan's Offline LCA를 사용한다. 모든 쿼리를 사전에 수집하고, DFS로 트리를 단 한 번 순회하며 Union-Find를 이용해 LCA를 일괄 처리한다. 자식 탐색이 끝날 때마다 해당 서브트리를 부모 집합으로 합친다.",
  "핵심_아이디어_단계": [
    {
      "제목": "① 오프라인 쿼리 저장",
      "설명": "입력 쿼리를 즉시 처리하지 않고, 두 노드 U·V 각각의 인접 리스트에 상대 노드와 쿼리 인덱스를 저장한다. 이렇게 하면 DFS 중 특정 노드를 방문했을 때 관련 쿼리를 한 번에 처리할 수 있다.",
      "코드": "for (int i = 0; i < M; i++) {\n    int u, v;\n    cin >> u >> v;\n    queries[u].push_back({ v, i });\n    queries[v].push_back({ u, i });\n}"
    },
    {
      "제목": "② DFS 순회 및 Union 병합",
      "설명": "방문 배열로 트리를 하향 탐색하고, 자식 노드의 탐색이 완전히 끝나면 자식 집합을 현재 노드로 병합(Union)한다. 아직 탐색 중인 노드는 병합하지 않아야 올바른 LCA가 도출된다.",
      "코드": "void LCA(int curr) {\n    visited[curr] = true;\n    for (int next : adj[curr]) {\n        if (!visited[next]) {\n            LCA(next);\n            parent[next] = curr;\n        }\n    }\n}"
    },
    {
      "제목": "③ Find로 LCA 도출",
      "설명": "자식 탐색 종료 후 현재 노드의 쿼리를 확인한다. 상대 노드가 이미 방문됐다면 그 노드의 집합 대표(find 결과)가 두 노드의 LCA다.",
      "코드": "for (auto& query : queries[curr]) {\n    int tar = query.first;\n    if (visited[tar]) {\n        answers[query.second] = find(tar);\n    }\n}"
    }
  ]
}"""


# -----------------------------------------------------------------------
# 모델 초기화 (싱글턴)
# -----------------------------------------------------------------------

def _get_client():
    global _model
    if _model is not None:
        return _model

    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

    _model = genai.Client(api_key=api_key)
    return _model


# -----------------------------------------------------------------------
# 핵심 함수
# -----------------------------------------------------------------------

def analyze(readme, code: str) -> AnalysisResult:
    try:
        client = _get_client()
    except Exception as e:
        print(f"[WARN] 클라이언트 초기화 실패: {e}")
        return AnalysisResult()

    from google.genai import types

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=_build_user_prompt(readme, code),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=1.0,
                top_p=0.95,
            ),
        )
        raw = response.text
    except Exception as e:
        print(f"[WARN] API 호출 실패: {e}")
        return AnalysisResult()

    return _parse(raw)


def _build_user_prompt(readme, code: str) -> str:
    desc = (readme.description or "(없음)")[:1500]
    inp  = (readme.input_desc  or "(없음)")[:500]
    out  = (readme.output_desc or "(없음)")[:300]
    src  = (code or "(없음)")[:3000]

    return f"""\
다음 알고리즘 문제와 풀이를 분석해주세요.

## 문제 정보
- 제목: {readme.title}
- 분류: {', '.join(readme.classifications)}
- 성능: 메모리 {readme.memory} KB / 시간 {readme.time} ms

## 문제 설명
{desc}

## 입력
{inp}

## 출력
{out}

## 풀이 코드 (C++)
{src}
"""


def _parse(raw: str) -> AnalysisResult:
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        print(f"[WARN] JSON 파싱 실패. 원문:\n{raw[:300]}")
        return AnalysisResult()
    try:
        d = json.loads(m.group())
        steps = [
            AnalysisStep(
                제목=s.get("제목", ""),
                설명=s.get("설명", ""),
                코드=s.get("코드", ""),
            )
            for s in d.get("핵심_아이디어_단계", [])
        ]
        return AnalysisResult(
            목표               = d.get("목표", ""),
            입력_상태          = d.get("입력_상태", ""),
            핵심_조건          = d.get("핵심_조건", ""),
            시간_복잡도        = d.get("시간_복잡도", "O(?)"),
            핵심_아이디어_개요 = d.get("핵심_아이디어_개요", ""),
            핵심_아이디어_단계 = steps,
        )
    except json.JSONDecodeError as e:
        print(f"[WARN] JSON 디코드 오류: {e}\n원문:\n{raw[:300]}")
        return AnalysisResult()

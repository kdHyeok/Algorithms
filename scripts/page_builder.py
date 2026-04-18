import urllib.parse

GITHUB_BASE = "https://github.com/kdHyeok/Algorithms/tree/main"


def github_url(folder_path: str) -> str:
    normalized = folder_path.replace("\\", "/")
    encoded = urllib.parse.quote(normalized, safe="/")
    return f"{GITHUB_BASE}/{encoded}"


# --- Block helpers ---

def _rt(text: str) -> list:
    if not text:
        return [{"type": "text", "text": {"content": ""}}]
    return [{"type": "text", "text": {"content": text[i:i + 2000]}}
            for i in range(0, len(text), 2000)]


def _h2(text: str) -> dict:
    return {"object": "block", "type": "heading_2",
            "heading_2": {"rich_text": _rt(text)}}


def _h3(text: str) -> dict:
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": _rt(text)}}


def _paragraph(text: str) -> dict:
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": _rt(text)}}


def _paragraph_code(text: str) -> dict:
    """Paragraph with the text rendered as inline code."""
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{
                "type": "text",
                "text": {"content": text},
                "annotations": {"code": True},
            }]}}


def _bullet(text: str) -> dict:
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": _rt(text)}}


def _bullet_bold(bold_part: str, rest: str) -> dict:
    """Bullet with a bold prefix followed by normal text."""
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [
                {"type": "text", "text": {"content": bold_part},
                 "annotations": {"bold": True}},
                {"type": "text", "text": {"content": rest}},
            ]}}


def _bullet_link(url: str) -> dict:
    """Bullet containing a hyperlinked URL."""
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{
                "type": "text",
                "text": {"content": url, "link": {"url": url}},
            }]}}


def _divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


def _perf_bullet(bold_part: str, rest: str) -> dict:
    """Yellow-background bullet for performance stats."""
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {"type": "text", "text": {"content": bold_part},
                     "annotations": {"bold": True}},
                    {"type": "text", "text": {"content": rest}},
                ],
                "color": "yellow_background",
            }}


def _code_blocks(code: str, language: str = "c++") -> list:
    text = code if code else "// 코드 파일 없음"
    rich_text = [{"type": "text", "text": {"content": text[i:i + 2000]}}
                 for i in range(0, len(text), 2000)]
    return [{"object": "block", "type": "code",
             "code": {"rich_text": rich_text, "language": language}}]


# --- Main builder ---

def build_children(readme, code: str, folder_path: str, lang: str = "C++",
                   analysis=None) -> list:
    """
    analysis: ai_analyzer.AnalysisResult 인스턴스 (선택).
              전달 시 문제 조건·시간 복잡도·핵심 아이디어를 AI 생성 내용으로 채운다.
    """
    notion_lang = "c++" if "C++" in lang else lang.lower()
    representative_algo = readme.classifications[0] if readme.classifications else "알 수 없음"
    perf_memory = f"{readme.memory} KB" if readme.memory else "-"
    perf_time = f"{readme.time} ms" if readme.time else "-"

    # AI 분석 결과 또는 placeholder
    목표       = (analysis.목표        or "(비워둠)") if analysis else "(비워둠)"
    입력_상태  = (analysis.입력_상태   or "(비워둠)") if analysis else "(비워둠)"
    핵심_조건  = (analysis.핵심_조건   or "(비워둠)") if analysis else "(비워둠)"
    복잡도     = (analysis.시간_복잡도 or "O(?)") if analysis else "O(?)"

    blocks = []

    # 문제
    blocks.append(_h2("문제"))
    if readme.problem_url:
        blocks.append(_bullet_link(readme.problem_url))
    blocks.append(_paragraph(readme.description if readme.description else "(문제 설명 없음)"))
    if readme.input_desc:
        blocks.append(_h3("입력"))
        blocks.append(_paragraph(readme.input_desc))
    if readme.output_desc:
        blocks.append(_h3("출력"))
        blocks.append(_paragraph(readme.output_desc))
    blocks.append(_divider())

    # 문제 조건
    blocks.append(_h3("문제 조건"))
    blocks.append(_bullet_bold("목표: ", 목표))
    blocks.append(_bullet_bold("입력 상태: ", 입력_상태))
    blocks.append(_bullet_bold("핵심 조건: ", 핵심_조건))
    blocks.append(_divider())

    # 풀이
    blocks.append(_h2("풀이"))
    blocks.append(_h3("핵심 알고리즘"))
    blocks.append(_paragraph_code(representative_algo))
    blocks.append(_bullet_bold("시간 복잡도: ", 복잡도))
    blocks.append(_h3("핵심 아이디어"))
    if analysis and analysis.핵심_아이디어_개요:
        blocks.append(_paragraph(analysis.핵심_아이디어_개요))
        for step in analysis.핵심_아이디어_단계:
            if step.제목:
                blocks.append(_h3(step.제목))
            if step.설명:
                blocks.append(_paragraph(step.설명))
            if step.코드:
                blocks.extend(_code_blocks(step.코드, notion_lang))
    else:
        blocks.append(_paragraph("(비워둠)"))
    blocks.append(_divider())

    # 성능
    blocks.append(_h3("성능"))
    blocks.append(_perf_bullet("메모리 : ", perf_memory))
    blocks.append(_perf_bullet("시간 : ", perf_time))

    # 코드
    blocks.append(_h3(f"코드 ({lang})"))
    blocks.extend(_code_blocks(code, notion_lang))
    blocks.append(_divider())

    return blocks

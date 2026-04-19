import urllib.parse
from bs4 import BeautifulSoup, NavigableString

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


def _image_block(url: str) -> dict:
    return {"object": "block", "type": "image",
            "image": {"type": "external", "external": {"url": url}}}


def _plain_code_block(text: str) -> dict:
    rich_text = [{"type": "text", "text": {"content": text[i:i + 2000]}}
                 for i in range(0, len(text), 2000)]
    return {"object": "block", "type": "code",
            "code": {"rich_text": rich_text, "language": "plain text"}}


def html_to_notion_blocks(html: str) -> list:
    """HTML(BaekjoonHub README) → Notion 블록 리스트 변환.

    처리 규칙:
      <p>          → paragraph
      <pre>        → plain text code block (격자·예제 보존)
      <img>        → image block (외부 URL)
      <table>      이미지만 있는 행   → image blocks + 캡션 paragraph
                   <pre> 포함 행     → code block per cell + 텍스트
                   텍스트만          → Notion table block
      <ul>/<ol>    → bulleted list
      기타 블록    → plain text paragraph
    """
    if not html or not html.strip():
        return []

    soup = BeautifulSoup(html, "html.parser")
    blocks = []

    def _inline(node) -> str:
        return node.get_text(separator="").strip()

    def _process_table(table):
        all_pres = table.find_all("pre")
        all_imgs = table.find_all("img")

        if all_pres:
            # <pre> 포함 테이블: 셀마다 code block + 텍스트
            for tr in table.find_all("tr"):
                for td in tr.find_all(["td", "th"]):
                    pre = td.find("pre")
                    if pre:
                        t = pre.get_text()
                        if t.strip():
                            blocks.append(_plain_code_block(t))
                    else:
                        t = _inline(td)
                        if t:
                            blocks.append(_paragraph(t))

        elif all_imgs:
            # 이미지 테이블: image blocks → 캡션 paragraph
            for tr in table.find_all("tr"):
                imgs = tr.find_all("img")
                if imgs:
                    for img in imgs:
                        src = img.get("src", "")
                        if src:
                            blocks.append(_image_block(src))
                else:
                    texts = [_inline(td) for td in tr.find_all(["td", "th"])]
                    caption = " | ".join(t for t in texts if t)
                    if caption:
                        blocks.append(_paragraph(caption))

        else:
            # 순수 텍스트 테이블 → Notion table block
            rows = table.find_all("tr")
            if not rows:
                return
            max_cols = max(len(r.find_all(["td", "th"])) for r in rows)
            if max_cols == 0:
                return
            table_rows = []
            for row in rows:
                cells = row.find_all(["td", "th"])
                cell_rts = []
                for i in range(max_cols):
                    t = _inline(cells[i]) if i < len(cells) else ""
                    cell_rts.append([{"type": "text", "text": {"content": t[:2000]}}])
                table_rows.append({"type": "table_row",
                                   "table_row": {"cells": cell_rts}})
            blocks.append({
                "object": "block", "type": "table",
                "table": {
                    "table_width": max_cols,
                    "has_column_header": False,
                    "has_row_header": False,
                },
                "children": table_rows,
            })

    def process(node):
        if isinstance(node, NavigableString):
            t = str(node).strip()
            if t:
                blocks.append(_paragraph(t))
            return
        name = getattr(node, "name", None)
        if not name:
            return

        if name == "p":
            t = _inline(node)
            if t:
                blocks.append(_paragraph(t))
        elif name == "pre":
            t = node.get_text()
            if t.strip():
                blocks.append(_plain_code_block(t))
        elif name == "img":
            src = node.get("src", "")
            if src:
                blocks.append(_image_block(src))
        elif name in ("ul", "ol"):
            for li in node.find_all("li", recursive=False):
                t = _inline(li)
                if t:
                    blocks.append(_bullet(t))
        elif name == "table":
            _process_table(node)
        elif name in ("div", "section", "blockquote", "td", "th"):
            for child in node.children:
                process(child)
        elif name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            t = _inline(node)
            if t:
                blocks.append(_h3(t))
        else:
            t = _inline(node)
            if t:
                blocks.append(_paragraph(t))

    for child in soup.children:
        process(child)

    return blocks


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
    if readme.description_html:
        blocks.extend(html_to_notion_blocks(readme.description_html))
    elif readme.description:
        blocks.append(_paragraph(readme.description))
    else:
        blocks.append(_paragraph("(문제 설명 없음)"))
    if readme.input_desc_html or readme.input_desc:
        blocks.append(_h3("입력"))
        if readme.input_desc_html:
            blocks.extend(html_to_notion_blocks(readme.input_desc_html))
        else:
            blocks.append(_paragraph(readme.input_desc))
    if readme.output_desc_html or readme.output_desc:
        blocks.append(_h3("출력"))
        if readme.output_desc_html:
            blocks.extend(html_to_notion_blocks(readme.output_desc_html))
        else:
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

import re
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup


@dataclass
class ReadmeData:
    number: str = ""
    title: str = ""
    level: str = ""
    problem_url: str = ""
    memory: str = ""
    time: str = ""
    classifications: list = field(default_factory=list)
    submit_date: str = ""
    description: str = ""
    input_desc: str = ""
    output_desc: str = ""


def _strip_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # <br> → 명시적 줄바꿈
    for tag in soup.find_all("br"):
        tag.replace_with("\n")
    # 블록 요소 뒤에 빈 줄 삽입 (인라인 요소는 건드리지 않음)
    for tag in soup.find_all(["p", "div"]):
        tag.append("\n\n")
    text = soup.get_text(separator="")
    # 3개 이상 연속 줄바꿈 정리
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_section(text: str, section: str) -> str:
    pattern = rf"### {re.escape(section)}\s*(.*?)(?=\n###|\Z)"
    m = re.search(pattern, text, re.DOTALL)
    return m.group(1).strip() if m else ""


_LEVEL_PREFIXES = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ruby", "Unrated"]


def parse_readme(path: str) -> ReadmeData:
    content = Path(path).read_text(encoding="utf-8")
    data = ReadmeData()

    # Title line: # [Level] Title - Number
    m = re.match(r"#\s+\[([^\]]+)\]\s+(.*?)\s*-\s*(\d+)", content)
    if m:
        raw_level = m.group(1).strip()
        data.title = m.group(2).strip()
        data.number = m.group(3)
        for prefix in _LEVEL_PREFIXES:
            if raw_level.startswith(prefix):
                data.level = prefix
                break
        else:
            data.level = "Unrated"

    # Problem URL
    m = re.search(r"\[문제 링크\]\((https?://[^)]+)\)", content)
    if m:
        data.problem_url = m.group(1)

    # 성능 요약
    perf = _extract_section(content, "성능 요약")
    m = re.search(r"메모리:\s*([\d,]+)\s*KB", perf)
    if m:
        data.memory = m.group(1).replace(",", "")
    m = re.search(r"시간:\s*([\d,]+)\s*ms", perf)
    if m:
        data.time = m.group(1).replace(",", "")

    # 분류 — filter out Markdown blockquote lines (SWEA attribution)
    classifications_raw = _extract_section(content, "분류")
    filtered_lines = [ln for ln in classifications_raw.split("\n") if not ln.strip().startswith(">")]
    classifications_text = " ".join(filtered_lines)
    data.classifications = [c.strip() for c in classifications_text.split(",") if c.strip()]

    # 제출 일자
    data.submit_date = _extract_section(content, "제출 일자")

    # 문제 설명 / 입력 / 출력 (백준만 존재)
    desc_raw = _extract_section(content, "문제 설명")
    data.description = _strip_html(desc_raw) if desc_raw else ""

    input_raw = _extract_section(content, "입력")
    data.input_desc = _strip_html(input_raw) if input_raw else ""

    output_raw = _extract_section(content, "출력")
    data.output_desc = _strip_html(output_raw) if output_raw else ""

    return data

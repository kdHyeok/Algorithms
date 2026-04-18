"""
AI 분석 파이프라인 단일 문제 테스트

Usage:
    python scripts/test_ai.py              # 기본: 15686 치킨 배달
    python scripts/test_ai.py 11437        # 문제번호 지정
    python scripts/test_ai.py 11437 --post # Notion 페이지 생성까지

Required env vars:
    HF_TOKEN            HuggingFace API 토큰
    NOTION_TOKEN        (--post 사용 시)
    NOTION_DATABASE_ID  (--post 사용 시)
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# .env 자동 로드 (로컬 실행 편의)
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from repo_scanner import scan_repo
from readme_parser import parse_readme
from ai_analyzer import analyze
from page_builder import build_children
from notion_sync import build_properties


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("number", nargs="?", default="15686", help="문제 번호 (기본: 15686)")
    parser.add_argument("--post", action="store_true", help="Notion에 실제 페이지 생성")
    args = parser.parse_args()

    repo_root = str(Path(__file__).parent.parent)
    problems = scan_repo(repo_root)
    problem = next((p for p in problems if p.number == args.number), None)

    if not problem:
        print(f"[ERROR] 문제 {args.number}를 레포에서 찾을 수 없습니다.")
        sys.exit(1)

    print(f"대상 문제: [{problem.site}] {problem.number}. {problem.title} ({problem.level})")
    print("─" * 60)

    readme = parse_readme(problem.readme_path)
    code = Path(problem.code_path).read_text(encoding="utf-8") if problem.code_path else ""

    # AI 분석
    print("AI 분석 중...")
    analysis = analyze(readme, code)

    print("\n[AI 분석 결과]")
    print(f"  목표       : {analysis.목표}")
    print(f"  입력 상태  : {analysis.입력_상태}")
    print(f"  핵심 조건  : {analysis.핵심_조건}")
    print(f"  시간 복잡도: {analysis.시간_복잡도}")
    print(f"  핵심 아이디어 개요:\n    {analysis.핵심_아이디어_개요}")
    for i, step in enumerate(analysis.핵심_아이디어_단계, 1):
        print(f"  단계 {i}: {step.제목}")
        print(f"    설명: {step.설명}")
        print(f"    코드: {step.코드}")

    if not args.post:
        print("\n--post 플래그 없음: Notion 등록 생략")
        return

    # Notion 페이지 생성
    from notion_api import get_registered_numbers, create_notion_page
    import time

    registered = get_registered_numbers()
    if problem.number in registered:
        print(f"\n[SKIP] 이미 Notion에 등록된 문제입니다: {problem.number}")
        return

    lang = "C++" if problem.code_path and Path(problem.code_path).suffix in (".cc", ".cpp") else "C++"
    properties = build_properties(problem, readme, analysis=analysis)
    children = build_children(readme, code, problem.folder_path, lang, analysis=analysis)
    create_notion_page(properties, children)
    print(f"\n[OK] Notion 페이지 생성 완료: [{problem.site}] {problem.number}. {problem.title}")


if __name__ == "__main__":
    main()

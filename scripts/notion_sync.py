"""
BaekjoonHub → Notion DB 자동 동기화 메인 스크립트

Usage:
    python scripts/notion_sync.py            # 실제 등록
    python scripts/notion_sync.py --dry-run  # 감지만 (Notion 변경 없음)

Required env vars:
    NOTION_TOKEN          Notion Integration token
    NOTION_DATABASE_ID    Notion Database ID (no dashes)
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Allow sibling modules to be imported when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repo_scanner import scan_repo
from readme_parser import parse_readme
from notion_api import get_registered_numbers, create_notion_page
from tag_mapper import map_tags
from page_builder import build_children


def _language_from_path(code_path: str) -> str:
    if not code_path:
        return "C++"
    ext = Path(code_path).suffix.lower()
    return {".cc": "C++", ".cpp": "C++", ".py": "Python", ".java": "Java", ".c": "C"}.get(ext, "C++")


def build_properties(problem, readme) -> dict:
    lang = _language_from_path(problem.code_path)
    tags = map_tags(readme.classifications)

    props = {
        "제목": {"title": [{"text": {"content": f"[{problem.number}] {problem.title}"}}]},
        "문제 사이트": {"select": {"name": problem.site}},
        "문제 레벨": {"select": {"name": problem.level}},
        "태그": {"multi_select": [{"name": t} for t in tags]},
        "사용 언어": {"select": {"name": lang}},
        "포스팅 상태": {"status": {"name": "시작 전"}},
        "포스팅 수준": {"select": {"name": "코드만"}},
    }
    if readme.problem_url:
        props["문제 주소"] = {"url": readme.problem_url}
    return props


def main() -> None:
    parser = argparse.ArgumentParser(description="BaekjoonHub → Notion DB 동기화")
    parser.add_argument("--dry-run", action="store_true",
                        help="Notion에 등록하지 않고 미등록 문제 목록만 출력")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    problems = scan_repo(repo_root)
    print(f"레포 스캔 완료: {len(problems)}개 문제 발견")

    if args.dry_run:
        registered = set()
        if os.environ.get("NOTION_TOKEN"):
            registered = get_registered_numbers()
            print(f"Notion 기존 등록: {len(registered)}개")
        else:
            print("[INFO] NOTION_TOKEN 없음 — 전체 문제를 신규로 간주합니다")

        new_problems = [p for p in problems if p.number not in registered]
        print(f"신규 등록 대상: {len(new_problems)}개")
        for p in new_problems:
            print(f"  [{p.site}] {p.number}. {p.title} ({p.level})")
        print("--dry-run 모드: Notion 등록 생략")
        return

    registered = get_registered_numbers()
    print(f"Notion 기존 등록: {len(registered)}개")

    new_problems = [p for p in problems if p.number not in registered]
    print(f"신규 등록 대상: {len(new_problems)}개")

    failed = 0
    for problem in new_problems:
        try:
            readme = parse_readme(problem.readme_path)
            code = Path(problem.code_path).read_text(encoding="utf-8") if problem.code_path else ""
            lang = _language_from_path(problem.code_path)
            properties = build_properties(problem, readme)
            children = build_children(readme, code, problem.folder_path, lang)
            create_notion_page(properties, children)
            print(f"[OK] [{problem.site}] {problem.number}. {problem.title}")
            time.sleep(0.35)
        except Exception as e:
            print(f"[ERROR] [{problem.site}] {problem.number}. {problem.title}: {e}",
                  file=sys.stderr)
            failed += 1

    print(f"\n동기화 완료: {len(new_problems) - failed}개 신규 등록, {failed}개 실패")
    if failed > 0 and failed == len(new_problems):
        sys.exit(1)


if __name__ == "__main__":
    main()

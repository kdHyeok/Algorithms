import os
import re
from dataclasses import dataclass


@dataclass
class ProblemEntry:
    number: str
    title: str
    level: str
    site: str          # "백준" or "SWEA"
    folder_path: str   # relative to repo root
    readme_path: str
    code_path: str     # empty string if not found


def _find_code_file(folder: str) -> str:
    for f in os.listdir(folder):
        if f.endswith(".cc") or f.endswith(".cpp"):
            return os.path.join(folder, f)
    return ""


def _extract_number_from_dirname(dirname: str):
    m = re.match(r"(\d+)\.", dirname)
    return m.group(1) if m else None


def _extract_level_from_dirname(dirname: str) -> str:
    m = re.search(r"\((\w+)\)\s*$", dirname)
    return m.group(1) if m else "Unrated"


def _extract_title_from_dirname(dirname: str) -> str:
    # Remove leading "number. " and trailing " (level)"
    s = re.sub(r"^\d+\.\s*", "", dirname)
    s = re.sub(r"\s*\(\w+\)\s*$", "", s)
    return s.strip()


def _scan_site(base_dir: str, site: str, repo_root: str) -> list:
    entries = []
    if not os.path.isdir(base_dir):
        return entries

    for dirname in os.listdir(base_dir):
        folder = os.path.join(base_dir, dirname)
        if not os.path.isdir(folder):
            continue

        number = _extract_number_from_dirname(dirname)
        if not number:
            continue

        readme = os.path.join(folder, "README.md")
        if not os.path.isfile(readme):
            print(f"[WARN] README.md 없음: {folder}")
            continue

        code = _find_code_file(folder)
        level = _extract_level_from_dirname(dirname)
        title = _extract_title_from_dirname(dirname)
        rel_path = os.path.relpath(folder, repo_root)

        entries.append(ProblemEntry(
            number=number,
            title=title,
            level=level,
            site=site,
            folder_path=rel_path,
            readme_path=readme,
            code_path=code,
        ))

    return entries


def scan_repo(repo_root: str = ".") -> list:
    baekjoon_dir = os.path.join(repo_root, "백준", "C++17")
    swea_dir = os.path.join(repo_root, "SWEA", "C++")

    entries = []
    entries.extend(_scan_site(baekjoon_dir, "백준", repo_root))
    entries.extend(_scan_site(swea_dir, "SWEA", repo_root))
    return entries

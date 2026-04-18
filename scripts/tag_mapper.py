TAG_MAP = {
    # 백준 한국어 분류
    "그래프 이론": "그래프",
    "트리": "트리",
    "최소 공통 조상": "LCA",
    "너비 우선 탐색": "BFS",
    "깊이 우선 탐색": "DFS",
    "다이나믹 프로그래밍": "DP",
    "그리디 알고리즘": "그리디",
    "정렬": "정렬",
    "이분 탐색": "이분탐색",
    "구현": "구현",
    "세그먼트 트리": "세그먼트트리",
    "두 포인터": "투포인터",
    "슬라이딩 윈도우": "슬라이딩윈도우",
    "백트래킹": "백트래킹",
    "분리 집합": "유니온파인드",
    "최단 경로": "최단경로",
    "스택": "스택",
    "큐": "큐",
    "우선순위 큐": "힙",
    "해시를 사용한 집합과 맵": "해시",
    "문자열": "문자열",
    "수학": "수학",
    "시뮬레이션": "시뮬레이션",
    "비트마스킹": "비트마스킹",
    # SWEA 영문 분류
    "BFS": "BFS",
    "DFS": "DFS",
    "DP": "DP",
    # 오타 변형
    "백트레킹": "백트래킹",
}


def map_tags(classifications: list) -> list:
    result = []
    seen = set()
    for c in classifications:
        c = c.strip()
        tag = TAG_MAP.get(c, c)  # 매핑 없으면 원문 그대로 사용
        if tag and tag not in seen:
            result.append(tag)
            seen.add(tag)
    return result

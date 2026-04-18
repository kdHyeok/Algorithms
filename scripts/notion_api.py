import os
import re
import time

from notion_client import Client


def _client() -> Client:
    return Client(auth=os.environ["NOTION_TOKEN"])


def _db_id() -> str:
    # Support both NOTION_DATABASE_ID (GitHub Actions) and NOTION_DB_ID (local .env)
    db_id = os.environ.get("NOTION_DATABASE_ID") or os.environ.get("NOTION_DB_ID")
    if not db_id:
        raise KeyError("NOTION_DATABASE_ID 또는 NOTION_DB_ID 환경변수가 필요합니다")
    return db_id


def get_registered_numbers() -> set:
    client = _client()
    db_id = _db_id()
    registered = set()
    cursor = None

    while True:
        kwargs = {"database_id": db_id, "page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor

        response = _query_with_retry(client, **kwargs)

        for page in response["results"]:
            title_prop = page["properties"].get("제목", {})
            title_items = title_prop.get("title", [])
            if title_items:
                text = "".join(t.get("plain_text", "") for t in title_items)
                m = re.match(r"\[(\d+)\]", text)
                if m:
                    registered.add(m.group(1))

        if not response.get("has_more"):
            break
        cursor = response["next_cursor"]

    return registered


def _query_with_retry(client: Client, **kwargs) -> dict:
    for attempt in range(3):
        try:
            return client.databases.query(**kwargs)
        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limited" in err.lower():
                print(f"[WARN] Rate limited, 60초 대기 후 재시도 ({attempt + 1}/3)")
                time.sleep(60)
            else:
                raise
    raise RuntimeError("Notion API 최대 재시도 초과")


def _create_with_retry(client: Client, **kwargs) -> dict:
    for attempt in range(3):
        try:
            return client.pages.create(**kwargs)
        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limited" in err.lower():
                print(f"[WARN] Rate limited, 60초 대기 후 재시도 ({attempt + 1}/3)")
                time.sleep(60)
            else:
                raise
    raise RuntimeError("Notion API 최대 재시도 초과")


def _append_with_retry(client: Client, block_id: str, children: list) -> None:
    for attempt in range(3):
        try:
            client.blocks.children.append(block_id=block_id, children=children)
            return
        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limited" in err.lower():
                print(f"[WARN] Rate limited, 60초 대기 후 재시도 ({attempt + 1}/3)")
                time.sleep(60)
            else:
                raise
    raise RuntimeError("Notion API 최대 재시도 초과")


def create_notion_page(properties: dict, children: list) -> None:
    client = _client()
    db_id = _db_id()

    first_batch = children[:100]
    remaining = children[100:]

    page = _create_with_retry(
        client,
        parent={"database_id": db_id},
        properties=properties,
        children=first_batch,
    )

    if remaining:
        page_id = page["id"]
        for i in range(0, len(remaining), 100):
            batch = remaining[i:i + 100]
            _append_with_retry(client, page_id, batch)
            time.sleep(0.35)

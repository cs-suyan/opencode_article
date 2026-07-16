import re
import json
import requests
from datetime import datetime, timedelta
from src.utils import normalize_title

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

SKIP_KEYWORDS = ["彩票", "彩民", "竞彩", "购彩", "中奖", "刮中", "兑奖", "专家推荐"]

# Priority classification keywords
_INTERNATIONAL = [
    "世界杯", "欧冠", "欧联", "欧协联", "英超", "西甲", "意甲", "德甲", "法甲",
    "NBA", "奥运", "世锦赛", "温网", "法网", "澳网", "美网", "F1", "世俱杯",
    "亚冠", "世乒赛", "世锦赛", "欧锦赛", "美洲杯", "亚洲杯", "非洲杯",
    "金球奖", "世界足球先生", "世预赛", "欧预赛",
    "法国", "阿根廷", "巴西", "德国", "西班牙", "意大利", "英格兰", "葡萄牙",
    "荷兰", "比利时", "克罗地亚", "摩洛哥", "埃及", "瑞士", "哥伦比亚",
    "姆巴佩", "梅西", "C罗", "内马尔", "哈兰德", "萨拉赫",
    "詹姆斯", "库里", "杜兰特", "字母哥", "约基奇", "东契奇",
    "德约", "纳达尔", "阿尔卡拉斯",
]

_DOMESTIC = [
    "中超", "CBA", "国足", "中国男足", "中国女足", "中国女排", "中国男篮",
    "全锦赛", "全运会", "亚运会", "亚运", "亚冠",
    "国乒", "王楚钦", "孙颖莎", "樊振东", "马龙", "陈梦", "王曼昱",
    "泰山队", "申花", "国安", "海港", "蓉城", "浙江队",
    "上海男篮", "广东男篮", "辽宁男篮", "新疆男篮",
    "周琦", "郭艾伦", "张镇麟", "杨瀚森",
    "郑钦文", "张之臻", "王欣瑜", "吴易昺",
]

_DOMESTIC_LEAGUES = [
    "中甲", "中乙", "WCBA", "排超", "乒超",
]


def _classify_priority(title: str) -> int:
    for kw in _INTERNATIONAL:
        if kw in title:
            return 0
    for kw in _DOMESTIC:
        if kw in title:
            return 1
    for kw in _DOMESTIC_LEAGUES:
        if kw in title:
            return 1
    return 2


def fetch_netease_sports(top_n: int = 10) -> list[dict]:
    try:
        api_url = f"https://3g.163.com/touch/reconstruct/article/list/BA8E6OEOwangning/0-{top_n * 2}.html"
        resp = requests.get(api_url, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"

        raw = resp.text.strip()
        if raw.startswith("artiList("):
            raw = raw[9:]
        if raw.endswith(")"):
            raw = raw[:-1]

        data = json.loads(raw)
        articles = data.get("BA8E6OEOwangning", [])

        cutoff = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

        seen = set()
        items = []
        for art in articles:
            title = art.get("title", "").strip()
            ptime = art.get("ptime", "")[:10]
            if not title or len(title) < 8:
                continue
            if ptime < cutoff:
                continue
            if any(kw in title for kw in SKIP_KEYWORDS):
                continue
            key = normalize_title(title)
            if key and key not in seen:
                seen.add(key)
                priority = _classify_priority(title)
                items.append({
                    "title": title,
                    "source": "netease_sports",
                    "hot_value": art.get("commentCount", 0),
                    "priority": priority,
                })

        # Sort by priority (0=international first), then by hot_value descending
        items.sort(key=lambda x: (x["priority"], -x.get("hot_value", 0)))

        return items[:top_n]
    except Exception as e:
        print(f"[netease_sports] 采集失败: {e}")
        return []


PLATFORM_MAP = {
    "netease_sports": fetch_netease_sports,
}


def collect_all(platforms: list[str], top_n: int = 10) -> list[dict]:
    all_items = []
    for platform in platforms:
        fetcher = PLATFORM_MAP.get(platform)
        if fetcher:
            items = fetcher(top_n)
            all_items.extend(items)
            print(f"[{platform}] 采集到 {len(items)} 条热点")
    return all_items


def deduplicate(items: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        key = normalize_title(item["title"])
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    return unique

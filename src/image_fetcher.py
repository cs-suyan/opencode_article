import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}


def search_images(keyword: str, count: int = 5) -> list[str]:
    try:
        resp = requests.get(
            "https://www.bing.com/images/search",
            params={"q": keyword, "count": count, "form": "HDRSC2"},
            headers=HEADERS,
            timeout=10,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        urls = []
        selectors = ["img.mimg", "img[class*='img']", "a.thumb img", "img[src*='http']"]
        for sel in selectors:
            for img in soup.select(sel):
                src = img.get("src") or img.get("data-src") or ""
                if src.startswith("http") and src not in urls:
                    urls.append(src)
            if urls:
                break
        return urls[:count]
    except Exception as e:
        print(f"[image] 搜索图片失败: {e}")
        return []


def pick_images(keywords: list[str], total: int = 3) -> list[tuple[str, str]]:
    result = []
    for i in range(total):
        kw = keywords[i % len(keywords)]
        imgs = search_images(kw, count=3)
        if imgs:
            result.append((imgs[0], kw))
    return result

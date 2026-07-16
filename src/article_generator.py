import re
import json
import requests
from src.image_fetcher import pick_images


class ArticleGenerator:
    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn/v1",
                 model: str = "deepseek-ai/DeepSeek-V4-Flash", max_tokens: int = 8192,
                 temperature: float = 0.8):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def _word_count_guideline(self, rank: int) -> str:
        if rank == 0:
            return "1000（该热点排名第一，影响力极大，需要深度分析，接近1000字）"
        elif rank <= 2:
            return "800~1000（该热点排名靠前，影响力较大，建议800~1000字）"
        elif rank <= 5:
            return "600~800（该热点有一定影响力，建议600~800字）"
        else:
            return "500~600（该热点影响力一般，建议500~600字）"

    def generate(self, news_title: str, rank: int = 0, keywords: list[str] | None = None) -> dict:
        word_target = self._word_count_guideline(rank)
        from datetime import datetime
        now_str = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        ARTICLE_MAX_WORDS = 800
        prompt = (
            f"你是一个聊体育贼溜的评论员。"
            f"现在给你一个体育新闻标题，你写一篇读着像饭桌上聊天的评论。\n\n"
            f"## 死命令（一条都不准违反）\n"
            f"- 不准编：文章里每一个比分、每一句话，都得是原标题里有的。多一个字都不行。\n"
            f"- 不准装：别写\"我当年\"\"我认识\"\"我见过\"——读者不关心你谁。\n"
            f"- 不准用过期信息：只聊{now_str}这个时间点的事。\n"
            f"- 不准用这些词：在当今社会、随着时代发展、众所周知、值得一提的是、不可否认、从某种程度来说、综上所述、总而言之。一个都不行。\n"
            f"- 不准用任何承接词和过渡词：首先、其次、最后、不过、但是、可是、然而、却、虽然、尽管、因为、所以、因此、与此同时、另外、此外、换句话说、也就是说、值得注意的是、毫无疑问。一个都不许出现。段落之间直接硬接。\n\n"
            f"原标题：{news_title}\n"
            f"字数目标：{word_target}\n\n"
            f"## 怎么写\n"
            f"1. 字数控制在{ARTICLE_MAX_WORDS}字以内。像跟朋友聊天一样，怎么说话就怎么写。不拽词，不掉书袋。\n"
            f"2. 标题要抓人，跟原标题完全不同，但说的是同一件事。\n"
            f"3. 段落长短自己把控。该细说的时候放开聊，该收住的时候——\n"
            f"   几个字就是一排，砸下去就得让人停一下。\n"
            f"4. 内容贴住原标题写。原题说了什么，你就聊什么。原题没说的，你别补。\n"
            f"5. 把网上球迷的真实反应、精彩段子、名场面揉进去，让文章有烟火气。\n"
            f"6. 文章里插2~3张图片占位标记，格式：<!--img:图片描述-->\n"
            f"7. 提取3-5个关键词，涵盖人物、事件、核心议题\n"
            f"8. 严格按以下格式输出，不要多一个字：\n\n"
            f"TITLE:你的原创标题\n"
            f"CONTENT:你的文章正文（含<!--img:关键词-->标记）\n"
            f"KEYWORDS:关键词1，关键词2，关键词3"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False,
        }
        import time
        for attempt in range(3):
            try:
                resp = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=180,
                )
                resp.raise_for_status()
                break
            except Exception as e:
                if attempt == 2:
                    raise
                print(f"[API] 第{attempt+1}次失败，3秒后重试: {e}")
                time.sleep(3)
        data = resp.json()
        raw = data["choices"][0]["message"]["content"].strip()
        return self._parse_and_embed(raw, news_title, keywords)

    def _parse_and_embed(self, text: str, news_title: str, keywords: list[str] | None) -> dict:
        title = ""
        content = ""
        kw = ""

        m = re.search(r'TITLE:(.*?)(?:\n|$)', text)
        if m:
            title = m.group(1).strip()

        m = re.search(r'CONTENT:(.*?)KEYWORDS:', text, re.DOTALL)
        if m:
            content = m.group(1).strip()

        m = re.search(r'KEYWORDS:(.*?)$', text, re.DOTALL)
        if m:
            kw = m.group(1).strip()

        if not title:
            fallback = re.search(r'^(.*?)(?:\n|$)', text)
            if fallback:
                title = fallback.group(1).strip()

        embedded = self._embed_images(content if content else text, news_title, keywords)

        return {
            "title": title or news_title,
            "content": embedded,
            "keywords": kw,
        }

    def _embed_images(self, content: str, news_title: str, keywords: list[str] | None) -> str:
        placeholders = re.findall(r'<!--img:(.*?)-->', content)
        if not placeholders:
            descs = [news_title, "新闻热点头图", "事件现场"]
            images = pick_images(descs, total=2)
            return self._insert_images_raw(content, images)

        images = pick_images(placeholders, total=len(placeholders))
        for desc, (img_url, _) in zip(placeholders, images):
            tag = f'<!--img:{desc}-->'
            replacement = f'\n\n![{desc}]({img_url})\n\n*图片来源网络*\n\n'
            content = content.replace(tag, replacement, 1)

        remaining = [m for m in re.findall(r'<!--img:(.*?)-->', content) if m]
        for r in remaining:
            content = content.replace(f'<!--img:{r}-->', '')

        return content

    def _insert_images_raw(self, content: str, images: list[tuple[str, str]]) -> str:
        paragraphs = content.split('\n\n')
        result = []
        inserted = 0
        for i, para in enumerate(paragraphs):
            result.append(para)
            if inserted < len(images) and i in [0, max(1, len(paragraphs) // 3)]:
                img_url, kw = images[inserted]
                result.append(f'\n\n![{kw}]({img_url})\n\n*图片来源网络*')
                inserted += 1
        return '\n\n'.join(result)

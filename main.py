import os
import random
import toml
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from src.news_collector import collect_all, deduplicate
from src.article_generator import ArticleGenerator
from src.file_saver import FileSaver

load_dotenv()


def load_config() -> dict:
    config_path = Path("config.toml")
    if not config_path.exists():
        raise FileNotFoundError("config.toml not found")
    cfg = toml.load(config_path)

    env_key = os.getenv("LLM_API_KEY")
    if env_key:
        cfg.setdefault("llm", {})["api_key"] = env_key

    return cfg


def build_hot_news_section(items: list[dict]) -> str:
    lines = ["\n\n---\n", "## 今日热点速览\n"]
    for i, item in enumerate(items, 1):
        source = item.get("source", "未知")
        title = item.get("title", "")
        hot = item.get("hot_value", 0)
        if hot:
            lines.append(f"{i}. [{source}] {title}（热度: {hot}）")
        else:
            lines.append(f"{i}. [{source}] {title}")
    return "\n".join(lines)


def main():
    config = load_config()

    llm_cfg = config["llm"]
    news_cfg = config["news"]
    output_cfg = config["output"]

    generator = ArticleGenerator(
        api_key=llm_cfg["api_key"],
        base_url=llm_cfg.get("base_url", "https://api.siliconflow.cn/v1"),
        model=llm_cfg.get("model", "deepseek-ai/DeepSeek-V4-Flash"),
        max_tokens=llm_cfg.get("max_tokens", 8192),
        temperature=llm_cfg.get("temperature", 0.8),
    )

    file_saver = FileSaver(base_dir=output_cfg.get("directory", "output"))

    print("=" * 40)
    print("热点新闻采集开始...")
    print("=" * 40)

    platforms = news_cfg.get("platforms", ["netease_sports"])
    top_n = news_cfg.get("top_n", 10)

    all_items = collect_all(platforms, top_n)
    unique_items = deduplicate(all_items)

    print(f"\n去重后共 {len(unique_items)} 条热点")

    if not unique_items:
        print("没有采集到热点，退出")
        return

    for idx, item in enumerate(unique_items):
        item["rank"] = idx

    hot_news_footer = build_hot_news_section(unique_items)

    random.shuffle(unique_items)

    for item in unique_items:
        original_title = item["title"]
        print(f"\n尝试选题：{original_title}")

        if file_saver.already_exists(original_title):
            print(f"  -> 今日已生成过，跳过")
            continue

        print(f"  -> 开始生成文章...")
        result = generator.generate(
            news_title=original_title,
            rank=item.get("rank", 5),
            keywords=[original_title, item.get("source", "")],
        )

        ai_title = result["title"]
        ai_content = result["content"]

        time_str = datetime.now().strftime("%H%M%S")
        filename = f"{time_str}_{ai_title}"

        formatted = (
            f"# {ai_title}\n\n"
            f"> 参考文章：{original_title}\n\n"
            f"{ai_content}\n"
            f"{hot_news_footer}"
        )

        filepath = file_saver.save(formatted, filename)
        file_saver.mark_generated(original_title)
        print(f"  -> 文章已保存：{filepath}")
        return

    print("\n所有热点今日均已生成过，无新文章可生成")


if __name__ == "__main__":
    main()

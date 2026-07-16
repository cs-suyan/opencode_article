import os
import sys
import random
import toml
import threading
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from kivy.app import App
from kivy.clock import mainthread
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    from plyer import filechooser, share
    HAS_PLYER = True
except Exception:
    HAS_PLYER = False

from src.news_collector import collect_all, deduplicate
from src.article_generator import ArticleGenerator
from src.file_saver import FileSaver

load_dotenv()


def load_config() -> dict:
    cfg = toml.load("config.toml")
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


class ArticleGenApp(App):
    def build(self):
        self.config_data = load_config()
        self.file_saver = None
        self.is_running = False
        self._log_lines = []
        return self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical", padding=[10, 10, 10, 10], spacing=5)

        title_label = Label(
            text="AI体育新闻热点文章生成器",
            size_hint_y=0.08,
            font_size="20sp",
            bold=True,
        )
        root.add_widget(title_label)

        sv = ScrollView(size_hint_y=0.77)
        self.log_input = TextInput(
            text="",
            readonly=True,
            font_size="14sp",
            foreground_color=[0.9, 0.9, 0.9, 1],
            background_color=[0.1, 0.1, 0.1, 1],
        )
        sv.add_widget(self.log_input)
        root.add_widget(sv)

        btn_box = BoxLayout(size_hint_y=0.15, spacing=10)
        self.start_btn = Button(text="开始生成", on_press=lambda _: self.start_generation())
        view_btn = Button(text="查看文章", on_press=lambda _: self.show_articles())
        share_btn = Button(text="分享文章", on_press=lambda _: self.share_article())
        btn_box.add_widget(self.start_btn)
        btn_box.add_widget(view_btn)
        btn_box.add_widget(share_btn)
        root.add_widget(btn_box)

        return root

    @mainthread
    def append_log(self, text: str):
        self._log_lines.append(text)
        self.log_input.text = "\n".join(self._log_lines[-200:])

    def start_generation(self):
        if self.is_running:
            return
        self.is_running = True
        self._log_lines = []
        self.log_input.text = ""
        self.start_btn.disabled = True
        threading.Thread(target=self._run_generation, daemon=True).start()

    def _run_generation(self):
        try:
            config = self.config_data
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

            self.file_saver = FileSaver(base_dir=output_cfg.get("directory", "output"))

            self.append_log("=" * 30)
            self.append_log("热点新闻采集开始...")
            self.append_log("=" * 30)

            platforms = news_cfg.get("platforms", ["netease_sports"])
            top_n = news_cfg.get("top_n", 10)

            all_items = collect_all(platforms, top_n)
            unique_items = deduplicate(all_items)
            self.append_log(f"\n去重后共 {len(unique_items)} 条热点")

            if not unique_items:
                self.append_log("没有采集到热点，退出")
                return

            for idx, item in enumerate(unique_items):
                item["rank"] = idx

            hot_news_footer = build_hot_news_section(unique_items)

            random.shuffle(unique_items)

            for item in unique_items:
                original_title = item["title"]
                self.append_log(f"\n尝试选题：{original_title}")

                if self.file_saver.already_exists(original_title):
                    self.append_log("  -> 今日已生成过，跳过")
                    continue

                self.append_log("  -> 开始生成文章...")
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

                filepath = self.file_saver.save(formatted, filename)
                self.file_saver.mark_generated(original_title)
                self.append_log(f"  -> 文章已保存：{filepath}")
                return

            self.append_log("\n所有热点今日均已生成过，无新文章可生成")

        except Exception as e:
            self.append_log(f"\n错误：{e}")
            import traceback
            self.append_log(traceback.format_exc())
        finally:
            self.is_running = False
            self.start_btn.disabled = False

    def share_article(self):
        output_dir = self.config_data.get("output", {}).get("directory", "output")
        today_path = Path(output_dir) / datetime.now().strftime("%Y-%m-%d")
        files = []
        if today_path.exists():
            files = sorted(today_path.glob("*.md"))
            files = [f for f in files if f.name != ".registry.json"]

        if not files:
            popup = Popup(title="提示", content=Label(text="暂无文章可分享"), size_hint=[0.6, 0.4])
            popup.open()
            return

        content = "选择要分享的文章：\n\n"
        file_map = {}
        for i, f in enumerate(files[-10:], 1):
            line = f"{i}. {f.stem[:40]}\n"
            content += line
            file_map[str(i)] = f

        text_input = TextInput(text=content, readonly=True, font_size="14sp")
        btn_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        share_btn = Button(text="分享最新一篇")

        popup = Popup(
            title="分享文章",
            content=text_input,
            size_hint=[0.9, 0.8],
        )

        def do_share(instance):
            popup.dismiss()
            latest = files[-1]
            try:
                article_text = latest.read_text(encoding="utf-8")
                if HAS_PLYER:
                    share.share(title=latest.stem, text=article_text)
                else:
                    Path(Path(output_dir).parent / "share_temp.md").write_text(article_text, encoding="utf-8")
                    info = Popup(title="提示", content=Label(text="文件已导出到项目目录 share_temp.md"), size_hint=[0.6, 0.4])
                    info.open()
            except Exception as e:
                err = Popup(title="错误", content=Label(text=str(e)), size_hint=[0.7, 0.5])
                err.open()

        share_btn.bind(on_press=do_share)
        btn_layout.add_widget(share_btn)
        main_layout = BoxLayout(orientation="vertical")
        main_layout.add_widget(text_input)
        main_layout.add_widget(btn_layout)
        popup.content = main_layout
        popup.open()

    def show_articles(self):
        output_dir = self.config_data.get("output", {}).get("directory", "output")
        today_path = Path(output_dir) / datetime.now().strftime("%Y-%m-%d")
        files = []
        if today_path.exists():
            files = sorted(today_path.glob("*.md"))
            files = [f for f in files if f.name != ".registry.json"]

        content = "今日已生成的文章：\n\n" if files else "今日暂无文章\n"
        for f in files[-20:]:
            content += f"  {f.stem}\n"

        popup = Popup(
            title="已生成文章",
            content=TextInput(text=content, readonly=True, font_size="14sp"),
            size_hint=[0.9, 0.8],
        )
        popup.open()


if __name__ == "__main__":
    ArticleGenApp().run()

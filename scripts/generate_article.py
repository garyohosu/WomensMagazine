from datetime import date
from codex_client import ask_codex


def yaml_double_quote(value: str) -> str:
    """Return a YAML-safe double-quoted scalar."""
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", " ")
        .replace("\n", " ")
    )
    return f'"{escaped}"'


def generate_article(topic):
    today = date.today().isoformat()
    safe_topic = yaml_double_quote(topic)

    prompt = (
        f"「{topic}」というテーマで、日本の女性向けライフスタイル雑誌の記事を書いてください。\n\n"
        "【記事の要件】\n"
        "- 文字数: 1500〜2000文字\n"
        "- 読者: 20〜40代の日本人女性\n"
        "- 文体: フレンドリーで親しみやすい「です・ます」調\n"
        "- 構成: 見出し(##)を4〜5個使って読みやすく整理する\n\n"
        "【面白い記事にするための必須要素】\n"
        "1. 冒頭: 読者が共感するあるあるエピソードや驚きの事実から始める\n"
        "2. 具体的な数字・金額・時間を必ず入れる（例: 年間6万円節約、15分で完成）\n"
        "3. 失敗談や「実はこれが落とし穴」など本音トークを1つ以上入れる\n"
        "4. 今日からできるアクションを箇条書きで3〜5つ\n"
        "5. 読者が思わず友人に教えたくなる驚きのTipsを1つ入れる\n"
        "6. 締めは読者を元気にする前向きなメッセージで終わる\n\n"
        "以下のJekyll front matterから書き始めてください:\n"
        "---\n"
        f"title: {safe_topic}\n"
        f"date: {today}\n"
        "categories: lifestyle\n"
        "tags: [生活, 女性, おすすめ]\n"
        "layout: post\n"
        "---\n\n"
        "front matterの直後から記事本文をMarkdown形式で書いてください。"
    )

    return ask_codex(prompt)

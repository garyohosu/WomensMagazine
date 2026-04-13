from datetime import datetime, timezone, timedelta
from codex_client import ask_codex
from local_llm_client import ask_local_llm


def _fallback_article(topic: str, today: str, safe_topic: str) -> str:
    return (
        "---\n"
        f"title: {safe_topic}\n"
        f"date: {today}\n"
        "categories: lifestyle\n"
        "tags: [生活, 女性, おすすめ]\n"
        f"amazon_keyword: {safe_topic}\n"
        "amazon_product_url: \"\"\n"
        "amazon_image_url: \"\"\n"
        "layout: post\n"
        "---\n\n"
        f"{topic}は、忙しい毎日でも取り入れやすい工夫を積み重ねることで体感が変わります。\n\n"
        "## まず押さえたい基本\n\n"
        "最初から完璧を目指すより、5分でできる小さな習慣を続けるほうが効果的です。\n"
        "朝・昼・夜のどこに入れるかを決めると継続しやすくなります。\n\n"
        "## よくある失敗と対策\n\n"
        "情報を集めすぎて実行が止まるケースが多いです。\n"
        "『今日1つだけ試す』と決めて、翌日に振り返る流れを作ると失敗が減ります。\n\n"
        "## 今日からできるアクション\n\n"
        "- タイマーを5分に設定して着手する\n"
        "- 終わったら1行メモを残す\n"
        "- 週末にメモを見返して改善点を1つ決める\n\n"
        "## まとめ\n\n"
        "小さく始めて、続けながら整える。これが一番の近道です。\n"
        "完璧さより、今日の一歩を優先して進めていきましょう。\n"
    )


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
    jst = timezone(timedelta(hours=9))
    today = datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S %z")
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
        "【読みやすさのルール】\n"
        "- 1段落は3文以内に収める。長くなったら改行で段落を分ける\n"
        "- ## 見出しの直前は必ず空行を入れる\n"
        "- 箇条書きの前後も空行を入れる\n"
        "- 文章が続く場合は2〜3文ごとに改行を入れてテンポよく読めるようにする\n\n"
        "以下のJekyll front matterから書き始めてください:\n"
        "---\n"
        f"title: {safe_topic}\n"
        f"date: {today}\n"
        "categories: lifestyle\n"
        "tags: [生活, 女性, おすすめ]\n"
        f"amazon_keyword: {safe_topic}\n"
        "amazon_product_url: \"\"\n"
        "amazon_image_url: \"\"\n"
        "layout: post\n"
        "---\n\n"
        "front matterの直後から記事本文をMarkdown形式で書いてください。"
    )

    # 1) Local LLM draft -> Codex fallback -> deterministic fallback
    try:
        draft = ask_local_llm(prompt, purpose="draft")
    except Exception:
        try:
            draft = ask_codex(prompt)
        except Exception:
            return _fallback_article(topic, today, safe_topic)

    # 2) Codex CLI polishes structure/facts/tone for publish quality
    polish_prompt = (
        "次の下書きを、女性週刊誌風の読みやすい記事に整えてください。\n"
        "要件:\n"
        "- front matterは維持\n"
        "- ですます調\n"
        "- 見出しの流れを滑らかに\n"
        "- 冗長表現を削る\n"
        "- 箇条書きは読みやすく\n"
        "- 1500〜2200字を目安\n"
        "改善後の本文のみ返してください。\n\n"
        f"{draft}"
    )
    try:
        return ask_codex(polish_prompt, timeout=360)
    except Exception:
        # polish失敗時は下書きをそのまま返して全体停止を回避
        return draft

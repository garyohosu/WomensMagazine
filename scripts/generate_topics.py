from datetime import date
from codex_client import ask_codex
from json_utils import extract_json_value


def generate_topics(n=10):
    today = date.today().strftime("%Y年%m月%d日")

    prompt = (
        f"今日は{today}です。\n"
        "日本の女性向けライフスタイルマガジン用の記事トピックを考えてください。\n\n"
        "条件:\n"
        f"- 今日の季節・トレンドに合った{n}件\n"
        "- 節約・料理・掃除・収納・美容・健康・恋愛・ファッション・子育てなどから選ぶ\n"
        "- 読者が「これ読みたい！」と思えるキャッチーなタイトルにする\n"
        "- 具体的な数字や体験談を想起させるタイトルにする\n"
        "  例: 「月3万円の食費が1.8万円に！主婦が実践した7つの節約ワザ」\n\n"
        f"JSON配列形式で{n}件のトピック文字列のみを返してください。\n"
        '例: ["トピック1", "トピック2"]'
    )

    raw = ask_codex(prompt)
    topics = extract_json_value(raw, list)

    normalized_topics = [str(topic).strip() for topic in topics if str(topic).strip()]
    return normalized_topics[:n]


if __name__ == "__main__":
    print(generate_topics())

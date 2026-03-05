from codex_client import ask_codex
from json_utils import extract_json_value


def review(article):
    prompt = (
        "以下の記事を採点してください。\n\n"
        "【評価基準】\n"
        "- 読みやすさ・テンポ (25点)\n"
        "- 具体性・実用性 (25点)\n"
        "- 共感・エンタメ性 (25点)\n"
        "- 構成・文字数 (25点)\n\n"
        f"{article}\n\n"
        "JSON形式のみで返してください:\n"
        '{"score": 合計点数(0-100), "feedback": "具体的な改善点を日本語で"}'
    )

    raw = ask_codex(prompt)
    result = extract_json_value(raw, dict)

    score = int(result["score"])
    feedback = str(result["feedback"]).strip()
    score = max(0, min(100, score))
    return score, feedback

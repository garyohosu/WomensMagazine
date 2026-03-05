from codex_client import ask_codex


def revise(article, feedback):
    prompt = (
        "以下のフィードバックをもとに記事を改善してください。\n"
        "front matter (---で囲まれた部分) はそのまま維持してください。\n"
        "改善した記事全文のみを返してください。説明は不要です。\n\n"
        f"【フィードバック】\n{feedback}\n\n"
        f"【記事】\n{article}"
    )

    return ask_codex(prompt)

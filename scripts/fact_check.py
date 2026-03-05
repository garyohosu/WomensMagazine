from codex_client import ask_codex


def fact_check(article):
    prompt = (
        "以下の記事を事実確認してください。\n"
        "誤った情報・不正確な数値・古い情報があれば正確な内容に修正してください。\n"
        "front matter (---で囲まれた部分) はそのまま維持してください。\n"
        "修正済みの記事全文のみを返してください。説明文は不要です。\n\n"
        f"{article}"
    )

    return ask_codex(prompt)

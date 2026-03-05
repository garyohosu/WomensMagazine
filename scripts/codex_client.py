"""
Codex CLI wrapper for text generation.
ChatGPT Plus の定額プランで動作。API キー不要。
認証は `codex auth` でログイン済みの ~/.codex/auth.json を使う。
"""
import subprocess
import tempfile
import os


def ask_codex(prompt: str, timeout: int = 300) -> str:
    """
    Codex CLI でテキストを生成して返す。
    Codex にファイルへ書き込ませ、そのファイルを読み返す方式で
    クリーンなテキスト出力を取得する。
    API キーは不要（ChatGPT Plus の OAuth トークンを使用）。
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "output.txt")

        task = (
            f"{prompt}\n\n"
            f"Write your complete response to this file: {output_file}\n"
            "Output ONLY the requested content to that file. No extra commentary."
        )

        # OPENAI_API_KEY を環境から除外して実行（定額プランの OAuth 認証を使う）
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}

        result = subprocess.run(
            ["codex", "--approval-mode", "full-auto", "-q", task],
            cwd=tmpdir,
            timeout=timeout,
            env=env,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Codex CLI が失敗しました。`codex auth` でログインしているか確認してください。\n"
                f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
            )

        if not os.path.exists(output_file):
            raise RuntimeError("Codex CLI は正常終了しましたが、output.txt が生成されませんでした。")

        with open(output_file, "r", encoding="utf-8") as f:
            return f.read().strip()

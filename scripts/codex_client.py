"""Codex CLI wrapper (flat-rate OAuth session, no API key).
Falls back to local LLM when Codex is unavailable.
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path

from local_llm_client import ask_local_llm

ROOT = Path(__file__).resolve().parent.parent


def _load_timeout(default: int = 600) -> int:
    cfg_path = ROOT / "data/config.json"
    if not cfg_path.exists():
        return default
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        return int(cfg.get("codex", {}).get("timeout", default))
    except Exception:
        return default


def ask_codex(prompt: str, timeout: int = None) -> str:
    timeout = timeout or _load_timeout(420)
    output_file = None
    try:
        with tempfile.NamedTemporaryFile(prefix="wm_codex_", suffix=".txt", delete=False) as tf:
            output_file = tf.name

        result = subprocess.run(
            ["codex", "exec", "--output-last-message", output_file, "-"],
            input=prompt,
            timeout=timeout,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return ask_local_llm(prompt, purpose="draft")

        out = ""
        if output_file and os.path.exists(output_file):
            out = Path(output_file).read_text(encoding="utf-8").strip()
        if not out:
            out = (result.stdout or "").strip()
        if not out:
            return ask_local_llm(prompt, purpose="draft")
        return out
    finally:
        if output_file and os.path.exists(output_file):
            try:
                os.remove(output_file)
            except Exception:
                pass

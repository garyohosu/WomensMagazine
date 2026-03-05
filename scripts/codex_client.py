"""Codex CLI wrapper (flat-rate OAuth session, no API key)."""
import json
import subprocess
from pathlib import Path

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
    timeout = timeout or _load_timeout(600)
    result = subprocess.run(
        ["codex", "exec", prompt],
        timeout=timeout,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Codex CLI failed. Check `codex` login/session.\n"
            f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )
    out = (result.stdout or "").strip()
    if not out:
        raise RuntimeError("Codex CLI returned empty output")
    return out

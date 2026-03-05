import json
import time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent


def load_config() -> dict:
    p = ROOT / "data/config.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def ask_local_llm(prompt: str, purpose: str = "draft") -> str:
    cfg = load_config().get("local_llm", {})
    endpoint = cfg.get("endpoint", "http://localhost:11434").rstrip("/")
    fallback_endpoint = cfg.get("fallback_endpoint", "http://172.25.192.1:11434").rstrip("/")
    timeout = int(cfg.get("timeout", 180))
    retries = int(cfg.get("retries", 2))

    if purpose == "topic":
        model = cfg.get("topic_model", "phi3:mini")
    else:
        model = cfg.get("draft_model", "qwen2.5:7b")

    last_err = None
    for i in range(retries + 1):
        target = endpoint if i < retries else fallback_endpoint
        try:
            resp = requests.post(
                f"{target}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=timeout,
            )
            # fallback endpoint may not have the same model; try phi3 as last resort
            if resp.status_code >= 400 and model != "phi3:mini" and i == retries:
                resp = requests.post(
                    f"{target}/api/generate",
                    json={"model": "phi3:mini", "prompt": prompt, "stream": False},
                    timeout=timeout,
                )
            resp.raise_for_status()
            out = (resp.json().get("response") or "").strip()
            if out:
                return out
            last_err = RuntimeError("local llm empty response")
        except Exception as e:
            last_err = e
            if i < retries:
                time.sleep(1.2 * (i + 1))
    raise RuntimeError(f"local llm failed after retries: {last_err}")

import json
import time
from pathlib import Path

try:
    import requests
except Exception:
    requests = None

ROOT = Path(__file__).resolve().parent.parent


def load_config() -> dict:
    p = ROOT / "data/config.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def ask_local_llm(prompt: str, purpose: str = "draft") -> str:
    import os
    if os.getenv("GITHUB_ACTIONS"):
        raise RuntimeError("local llm skipped in GitHub Actions environment")
    if requests is None:
        raise RuntimeError(
            "local llm support requires the 'requests' package; use Codex fallback or install requirements.txt"
        )

    cfg = load_config().get("local_llm", {})
    endpoint = cfg.get("endpoint", "http://localhost:11434").rstrip("/")
    fallback_endpoint = cfg.get("fallback_endpoint", "http://172.25.192.1:11434").rstrip("/")
    base_timeout = int(cfg.get("timeout", 90))
    keep_alive = str(cfg.get("keep_alive", "45m"))
    retries_cfg = int(cfg.get("retries", 1))

    if purpose == "topic":
        timeout = min(base_timeout, 60)
        cold_start_timeout = min(int(cfg.get("cold_start_timeout", 120)), 90)
        retries = 1
    else:
        timeout = min(base_timeout, 120)
        cold_start_timeout = min(int(cfg.get("cold_start_timeout", max(timeout, 150))), 180)
        retries = min(retries_cfg, 1)

    if purpose == "topic":
        model = cfg.get("topic_model", "phi3:mini")
    else:
        model = cfg.get("draft_model", "qwen2.5:7b")

    last_err = None
    for i in range(retries + 1):
        target = endpoint if i < retries else fallback_endpoint
        try:
            timeout_eff = cold_start_timeout if i == 0 else timeout
            print(
                f"[local-llm] attempt={i+1}/{retries+1} purpose={purpose} model={model} target={target} timeout={timeout_eff}",
                flush=True,
            )
            resp = requests.post(
                f"{target}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False, "keep_alive": keep_alive},
                timeout=timeout_eff,
            )
            # fallback endpoint may not have the same model; try phi3 as last resort
            if resp.status_code >= 400 and model != "phi3:mini" and i == retries:
                resp = requests.post(
                    f"{target}/api/generate",
                    json={"model": "phi3:mini", "prompt": prompt, "stream": False, "keep_alive": keep_alive},
                    timeout=timeout_eff,
                )
            resp.raise_for_status()
            out = (resp.json().get("response") or "").strip()
            if out:
                print(f"[local-llm] success chars={len(out)}", flush=True)
                return out
            last_err = RuntimeError("local llm empty response")
        except Exception as e:
            last_err = e
            print(f"[local-llm] error attempt={i+1}: {e}", flush=True)
            if i < retries:
                time.sleep(1.2 * (i + 1))
    raise RuntimeError(f"local llm failed after retries: {last_err}")

from datetime import date
import re
from local_llm_client import ask_local_llm
from codex_client import ask_codex
from json_utils import extract_json_value


def _fallback_topics(n: int):
    today = date.today().strftime("%Y年%m月%d日")
    base = [
        f"{today}版：春の暮らしを軽くする5分習慣",
        f"{today}版：食費と時短を両立する1週間メニュー",
        f"{today}版：花粉シーズンのゆらぎ肌対策7ルール",
    ]
    return base[: max(1, n)]


def _normalize_topics(cands, n):
    out = []
    seen = set()
    for t in cands:
        s = str(t)
        s = re.sub(r"^[\-\d\.)\s]+", "", s)
        s = s.strip().strip('"').strip("'").strip().strip(",")
        s = s.strip("[]")
        s = s.replace("\u3000", " ").strip()

        # remove wrapper-like noise
        if not s or s in {"[", "]", "{" ,"}", ","}:
            continue
        if len(s) < 6:
            continue
        if re.fullmatch(r"[\W_]+", s):
            continue

        if s in seen:
            continue
        seen.add(s)
        out.append(s)
        if len(out) >= n:
            break
    return out


def _parse_non_json_list(raw: str):
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    # collect bullet/numbered lines
    candidates = [ln for ln in lines if re.match(r"^(?:[-*]|\d+[\.)])\s*", ln)]
    if candidates:
        return _normalize_topics(candidates, 20)
    return _normalize_topics(lines, 20)


def generate_topics(n=10):
    today = date.today().strftime("%Y年%m月%d日")

    prompt = (
        f"今日は{today}です。\n"
        "日本の女性向けライフスタイルマガジン用の記事トピックを考えてください。\n\n"
        "条件:\n"
        f"- 今日の季節・トレンドに合った{n}件\n"
        "- 節約・料理・掃除・収納・美容・健康・恋愛・ファッション・子育てなどから選ぶ\n"
        "- 読者が『これ読みたい！』と思えるキャッチーなタイトルにする\n"
        "- 具体的な数字や体験談を想起させるタイトルにする\n"
        "  例: 月3万円の食費が1.8万円に！主婦が実践した7つの節約ワザ\n\n"
        f"JSON配列形式で{n}件のトピック文字列のみを返してください。\n"
        '例: ["トピック1", "トピック2"]'
    )

    # 1) local llm first（失敗時は即Codex）
    try:
        raw = ask_local_llm(prompt, purpose="topic")
    except Exception:
        raw = ask_codex(prompt, timeout=180)

    try:
        topics = extract_json_value(raw, list)
        normalized_topics = _normalize_topics(topics, n)
    except Exception:
        normalized_topics = _parse_non_json_list(raw)

    # 2) codex fallback/complement
    if len(normalized_topics) < n:
        try:
            raw2 = ask_codex(prompt, timeout=180)
            try:
                topics2 = extract_json_value(raw2, list)
            except Exception:
                topics2 = _parse_non_json_list(raw2)
            normalized_topics = _normalize_topics(normalized_topics + topics2, n)
        except Exception:
            pass

    # 3) codex polish: make titles natural/clickable Japanese
    try:
        polish_prompt = (
            f"次のトピック案を、日本の女性向けライフスタイル記事タイトルとして自然な日本語に整えてください。"
            f"{n}件ちょうど、JSON配列のみで返答。\n\n"
            + "\n".join(f"- {t}" for t in normalized_topics[: max(n, len(normalized_topics))])
        )
        polished = ask_codex(polish_prompt, timeout=180)
        try:
            topics3 = extract_json_value(polished, list)
        except Exception:
            topics3 = _parse_non_json_list(polished)
        final_topics = _normalize_topics(topics3, n)
        if len(final_topics) >= n:
            return final_topics[:n]
    except Exception:
        pass

    result = normalized_topics[:n]
    if not result:
        return _fallback_topics(n)
    return result


if __name__ == "__main__":
    print(generate_topics())

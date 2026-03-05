from datetime import date
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
COVER_DIR = ROOT / "assets" / "covers"


def _slugify(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[\s　]+", "-", s)
    s = re.sub(r"[^\w\-ぁ-んァ-ン一-龥]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "untitled"


def _trim_title(title: str, max_len: int = 28) -> str:
    return title if len(title) <= max_len else title[: max_len - 1] + "…"


def _build_cover_svg(topic: str) -> str:
    today = date.today().isoformat()
    title = _trim_title(topic)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-label="{topic}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#fff1f6"/>
      <stop offset="100%" stop-color="#ffe3ef"/>
    </linearGradient>
    <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#ec4899"/>
      <stop offset="100%" stop-color="#f43f5e"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect x="64" y="60" width="1072" height="510" rx="28" fill="#ffffff" stroke="#fbcfe8" stroke-width="2"/>

  <text x="104" y="145" fill="#db2777" font-size="28" font-family="Noto Sans JP, Arial, sans-serif" letter-spacing="2">WOMEN'S WEEKLY STYLE</text>
  <rect x="104" y="165" width="420" height="6" rx="3" fill="url(#line)"/>

  <text x="104" y="285" fill="#881337" font-size="64" font-weight="700" font-family="Noto Sans JP, Arial, sans-serif">{title}</text>
  <text x="104" y="352" fill="#9d174d" font-size="34" font-family="Noto Sans JP, Arial, sans-serif">毎日の暮らしに、少しだけ新しいヒントを。</text>

  <text x="104" y="520" fill="#be185d" font-size="26" font-family="Noto Sans JP, Arial, sans-serif">{today}</text>
  <text x="965" y="520" fill="#be185d" font-size="26" font-family="Noto Sans JP, Arial, sans-serif">特集</text>
</svg>'''


def generate_image(topic):
    """Generate a deterministic local eyecatch image (SVG) and return site-relative path."""
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{date.today().isoformat()}-{_slugify(topic)}.svg"
    path = COVER_DIR / filename
    if not path.exists():
        path.write_text(_build_cover_svg(topic), encoding="utf-8")
    return f"/assets/covers/{filename}"


def insert_image_into_article(article, image_url):
    """front matterにimage URLを追加し、記事先頭に画像を挿入する。"""
    lines = article.split("\n")

    # Find closing --- of front matter
    fm_end = -1
    in_fm = False
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
            else:
                fm_end = i
                break

    if fm_end == -1:
        return f"![記事画像]({image_url})\n\n{article}"

    has_image = any(l.strip().startswith("image:") for l in lines[:fm_end])
    if not has_image:
        lines.insert(fm_end, f"image: {image_url}")
        fm_end += 1

    # Insert visual preview right after front matter if missing
    body_start = fm_end + 1
    if body_start < len(lines):
        marker = f"![記事画像]({image_url})"
        if marker not in "\n".join(lines[body_start:body_start + 5]):
            lines.insert(body_start + 1, f"\n{marker}\n")

    return "\n".join(lines)

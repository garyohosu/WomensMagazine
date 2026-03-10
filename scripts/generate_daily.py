import os
import re
import time
from datetime import date

from generate_topics import generate_topics
from generate_article import generate_article
from generate_image import generate_image, insert_image_into_article
from fact_check import fact_check
from review_article import review
from revise_article import revise

POSTS_DIR = os.path.join(os.path.dirname(__file__), "..", "_posts")
INVALID_FILENAME_CHARS = set('<>:"/\\|?*')


def sanitize_secret_like_text(article: str) -> str:
    """Redact secret-like strings before writing public markdown."""
    replacements = [
        (r"OPENAI_API_KEY\s*[:=]\s*\S+", "OPENAI_API_KEY=<REDACTED>"),
        (r"sk-[A-Za-z0-9]{20,}", "<REDACTED_OPENAI_KEY>"),
        (r"ghp_[A-Za-z0-9]{36}", "<REDACTED_GITHUB_TOKEN>"),
    ]
    redacted = article
    for pattern, repl in replacements:
        redacted = re.sub(pattern, repl, redacted, flags=re.IGNORECASE)
    return redacted


def slugify_title(title: str) -> str:
    """Create a filesystem-safe filename fragment from a topic title."""
    normalized = title.replace(" ", "_").replace("　", "_")
    cleaned = []
    for char in normalized:
        if char in INVALID_FILENAME_CHARS or ord(char) < 32:
            cleaned.append("_")
        else:
            cleaned.append(char)

    slug = "".join(cleaned)
    slug = slug.replace("..", "_")
    slug = re.sub(r"_+", "_", slug).strip("._")
    return slug or "untitled"


def build_post_path(title: str) -> str:
    filename = slugify_title(title)
    base_name = f"{date.today()}-{filename}.md"
    posts_root = os.path.abspath(POSTS_DIR)
    candidate = os.path.abspath(os.path.join(posts_root, base_name))

    if os.path.commonpath([posts_root, candidate]) != posts_root:
        raise ValueError("Unsafe post path detected.")

    suffix = 2
    while os.path.exists(candidate):
        candidate = os.path.abspath(
            os.path.join(posts_root, f"{date.today()}-{filename}-{suffix}.md")
        )
        suffix += 1

    return candidate


def publish(article, title):
    os.makedirs(POSTS_DIR, exist_ok=True)
    path = build_post_path(title)
    sanitized = sanitize_secret_like_text(article)
    if sanitized != article:
        print("Secret-like text detected and redacted before publish")
    with open(path, "w", encoding="utf-8") as f:
        f.write(sanitized)
    print(f"Published: {path}")


def _log(msg: str) -> None:
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def main():
    t0 = time.time()
    _log("START generate_daily")

    _log("STEP topics: generate_topics")
    topics = generate_topics(n=1)
    _log(f"STEP topics: done ({len(topics)} topics)")

    for t in topics:
        _log(f"=== Generating: {t} ===")
        try:
            s = time.time()
            _log("STEP article: generate_article")
            article = generate_article(t)
            _log(f"STEP article: done ({time.time() - s:.1f}s)")

            s = time.time()
            _log("STEP image: generate_image")
            image_url = generate_image(t)
            _log(f"STEP image: done ({time.time() - s:.1f}s)")

            article = insert_image_into_article(article, image_url)
            _log("STEP image: inserted into article")

            s = time.time()
            _log("STEP fact_check")
            article = fact_check(article)
            _log(f"STEP fact_check: done ({time.time() - s:.1f}s)")

            retry = 0
            while retry < 3:
                s = time.time()
                _log(f"STEP review: attempt {retry + 1}")
                score, feedback = review(article)
                _log(f"STEP review: done score={score} ({time.time() - s:.1f}s)")

                if score >= 80:
                    break

                _log(f"STEP revise: attempt {retry + 1}")
                s = time.time()
                article = revise(article, feedback)
                _log(f"STEP revise: done ({time.time() - s:.1f}s)")
                retry += 1

            s = time.time()
            _log("STEP publish")
            publish(article, t)
            _log(f"STEP publish: done ({time.time() - s:.1f}s)")
        except Exception as exc:
            _log(f"ERROR topic '{t}': {exc}")

    _log(f"END generate_daily ({time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()

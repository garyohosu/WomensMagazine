import os
import re
from datetime import date

from generate_topics import generate_topics
from generate_article import generate_article
from generate_image import generate_image, insert_image_into_article
from fact_check import fact_check
from review_article import review
from revise_article import revise

POSTS_DIR = os.path.join(os.path.dirname(__file__), "..", "_posts")
INVALID_FILENAME_CHARS = set('<>:"/\\|?*')


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
    with open(path, "w", encoding="utf-8") as f:
        f.write(article)
    print(f"Published: {path}")


def main():
    topics = generate_topics()
    print(f"Topics generated: {len(topics)}")

    for t in topics:
        print(f"\n=== Generating: {t} ===")
        try:
            article = generate_article(t)

            image_url = generate_image(t)
            article = insert_image_into_article(article, image_url)

            article = fact_check(article)

            retry = 0
            while retry < 3:
                score, feedback = review(article)
                print(f"Score: {score} | Feedback: {feedback}")

                if score >= 80:
                    break

                print(f"Revising (attempt {retry + 1})...")
                article = revise(article, feedback)
                retry += 1

            publish(article, t)
        except Exception as exc:
            print(f"Failed to generate topic '{t}': {exc}")


if __name__ == "__main__":
    main()

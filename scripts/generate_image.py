def generate_image(topic):
    """
    Placeholder image AI.
    将来的にDALL-EやStable Diffusionと連携予定。
    現在はunsplash.comのプレースホルダー画像URLを返す。
    """
    slug = topic.replace(" ", "-").replace("　", "-")
    image_url = f"https://source.unsplash.com/800x400/?{slug},lifestyle"
    return image_url


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
        # No front matter found, prepend image
        return f"![記事画像]({image_url})\n\n{article}"

    # Insert image field before closing ---
    lines.insert(fm_end, f"image: {image_url}")
    # Also add image after front matter
    lines.insert(fm_end + 2, f"\n![記事画像]({image_url})\n")

    return "\n".join(lines)

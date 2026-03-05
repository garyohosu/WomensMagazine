---
layout: default
title: ライフスタイル
permalink: /lifestyle/
---

<section class="mb-8">
  <h1 class="font-bold text-3xl text-rose-700 mb-2">ライフスタイル</h1>
  <p class="text-gray-600">毎日の暮らしをラクに、楽しくする記事をまとめています。</p>
</section>

{% assign posts = site.categories.lifestyle %}
{% if posts and posts.size > 0 %}
<div class="space-y-4">
  {% for post in posts %}
  <article class="bg-white rounded-xl shadow-md p-5">
    <h2 class="font-bold text-xl text-gray-900 mb-2">
      <a href="{{ post.url | relative_url }}" class="hover:text-rose-600 transition">{{ post.title }}</a>
    </h2>
    <p class="text-sm text-gray-400 mb-2">{{ post.date | date: "%Y年%m月%d日" }}</p>
    <p class="text-gray-600">{{ post.excerpt | strip_html | truncate: 140 }}</p>
  </article>
  {% endfor %}
</div>
{% else %}
<div class="bg-white rounded-xl shadow-md p-6 text-gray-500">
  まだ記事がありません。
</div>
{% endif %}

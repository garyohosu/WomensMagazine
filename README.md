
# WomensMagazine

AIエージェントが記事を生成するSEOメディア。

## Features
- 1日10記事自動生成
- AIレビュー
- ファクトチェック
- GitHub Pages公開
- 役割分担生成（Local LLM + Codex CLI定額）
  - Local LLM: トピック案出し・下書き生成
  - Codex CLI: 仕上げ・レビュー・修正
- Amazonアソシエイト導線（記事下に関連商品検索リンク）
- front matter に `amazon_product_url` と `amazon_image_url` を入れると、
  画像生成の代わりに商品画像リンクを記事冒頭に表示

## OpenClaw cron での運用手順

### 1. 事前準備（実行マシンで1回）
- Node.js をインストール
- Codex CLI をインストール: `npm install -g @openai/codex`
- Python（`py` コマンド）を使える状態にする
- Codex にログイン: `codex auth`

### 2. 手動実行コマンド（動作確認）
PowerShell で以下を実行:

```powershell
Set-Location C:\PROJECT\WomensMagazine
py scripts/generate_daily.py
git add _posts
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
  git commit -m "Add articles for $(Get-Date -Format yyyy-MM-dd)"
  git push
}
```

Linux / OpenClaw 側で動かすなら、user site-packages の混線を避けるため
`PYTHONNOUSERSITE=1 python3 scripts/generate_daily.py` を使う。

### 3. OpenClaw の cron に登録
OpenClaw 側の cron ジョブで、上記 PowerShell コマンドを毎日1回実行する設定にする。

### 4. 注意点
- GitHub Actions でも同じ生成を動かすと二重投稿になるため、OpenClaw cron を使う場合は GitHub Actions の定期実行を無効化してください。

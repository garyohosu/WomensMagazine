
# WomensMagazine

AIエージェントが記事を生成するSEOメディア。

## Features
- 1日10記事自動生成
- AIレビュー
- ファクトチェック
- GitHub Pages公開

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

### 3. OpenClaw の cron に登録
OpenClaw 側の cron ジョブで、上記 PowerShell コマンドを毎日1回実行する設定にする。

### 4. 注意点
- GitHub Actions でも同じ生成を動かすと二重投稿になるため、OpenClaw cron を使う場合は GitHub Actions の定期実行を無効化してください。

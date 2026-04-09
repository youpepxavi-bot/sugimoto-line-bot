# お肉膳スギモト LINE Bot
## 三井アウトレットパーク岡崎店 公式LINE

---

## 機能一覧

| 機能 | 概要 |
|------|------|
| ウェルカムメッセージ | 友だち追加時に自動で歓迎メッセージ + 初回来店クーポン送信 |
| リッチメニュー（6ボタン） | クーポン / スタンプカード / おすすめ / 誕生日登録 / お知らせ / 店舗情報 |
| 誕生日クーポン自動配信 | 毎朝09:00に誕生日のお客様へ自動でクーポンを送信 |
| キーワード自動応答 | 「クーポン」「アクセス」「メニュー」などに自動返答 |
| 一斉配信API | 新メニュー・キャンペーン告知をAPIで一斉送信 |
| ユーザーDB | 来店回数・誕生日・セグメント情報を管理（将来の活用に備える） |

---

## 技術スタック

- **言語**: Python 3.11+
- **フレームワーク**: FastAPI
- **LINE SDK**: line-bot-sdk-python v3
- **DB**: SQLite（本番はPostgreSQLへの移行も容易）
- **スケジューラー**: APScheduler
- **デプロイ**: Render（無料枠）

---

## ファイル構成

```
sugimoto-line-bot/
├── main.py                    # FastAPI アプリ本体・Webhookエンドポイント
├── database.py                # SQLite DB定義・ユーザー管理
├── scheduler.py               # 誕生日クーポン自動配信スケジューラー
├── generate_richmenu.py       # リッチメニュー画像生成 + API設定ツール
├── handlers/
│   ├── follow.py              # 友だち追加イベント処理
│   ├── postback.py            # リッチメニューボタン処理
│   └── message.py             # テキストメッセージ処理
├── templates/
│   └── messages.py            # 全メッセージテンプレート集
├── docs/
│   ├── line-developers-setup.md  # LINE Developers設定手順
│   ├── shop-card-setup.md        # ショップカード設定手順
│   └── message-templates.md      # 配信メッセージテンプレート集
├── render.yaml                # Renderデプロイ設定
├── requirements.txt
└── .env.example
```

---

## セットアップ手順

### 1. リポジトリのクローン（またはファイルコピー）

```bash
cd sugimoto-line-bot
```

### 2. 仮想環境の作成と依存パッケージのインストール

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して以下を設定（取得方法は `docs/line-developers-setup.md` 参照）：

```env
LINE_CHANNEL_SECRET=（チャネルシークレット）
LINE_CHANNEL_ACCESS_TOKEN=（チャネルアクセストークン）
```

### 4. ローカルで動作確認

```bash
python main.py
```

ブラウザで `http://localhost:8000` を開いて `{"status": "ok"}` が表示されればOK。

### 5. ngrokでローカルをLINEに繋ぐ（テスト用）

```bash
# ngrokのインストール（初回のみ）
# https://ngrok.com/ からダウンロード

ngrok http 8000
```

表示された `https://xxxx.ngrok.io` を LINE DevelopersのWebhook URLに設定：
```
https://xxxx.ngrok.io/callback
```

---

## リッチメニューの設定

### 画像生成のみ

```bash
python generate_richmenu.py --generate-image
# → richmenu.png が生成される（2500×1686px）
```

### 画像生成 + LINE API自動設定（一発セットアップ）

`.env` を設定済みの状態で実行：

```bash
python generate_richmenu.py --setup-all

# 既存のリッチメニューを削除してから設定する場合
python generate_richmenu.py --setup-all --clean
```

---

## Renderへのデプロイ手順

### 1. GitHubにプッシュ

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/yourusername/sugimoto-line-bot.git
git push -u origin main
```

### 2. Renderでデプロイ

1. [Render](https://render.com/) にサインアップ・ログイン
2. 「New」→「Web Service」
3. GitHubリポジトリを連携
4. `render.yaml` の設定が自動適用される
5. 「Environment」タブで以下を設定：
   - `LINE_CHANNEL_SECRET`
   - `LINE_CHANNEL_ACCESS_TOKEN`
6. 「Deploy」をクリック

### 3. デプロイ後の設定

Renderから発行されたURL（例：`https://sugimoto-line-bot.onrender.com`）を：
1. LINE DevelopersのWebhook URLに設定 (`/callback` 付き)
2. `.env` の `BASE_URL` に設定

---

## 管理用API

| エンドポイント | メソッド | 説明 |
|----------------|---------|------|
| `/` | GET | ヘルスチェック |
| `/health` | GET | ヘルスチェック詳細 |
| `/callback` | POST | LINE Webhook受信（自動） |
| `/admin/broadcast` | POST | 一斉配信（新メニュー・キャンペーン） |
| `/admin/users/count` | GET | 登録ユーザー数確認 |

### 一斉配信の使い方

```bash
# 新メニュー告知
curl -X POST https://sugimoto-line-bot.onrender.com/admin/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "type": "new_menu",
    "menu_name": "黒毛和牛 特上カルビ",
    "description": "口の中でとろける霜降りの旨み",
    "price": "3,300円（税込）"
  }'

# キャンペーン告知
curl -X POST https://sugimoto-line-bot.onrender.com/admin/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "type": "campaign",
    "title": "夏の黒毛和牛フェア",
    "body": "この夏だけの特別コース",
    "period": "7月1日〜8月31日"
  }'
```

---

## 誕生日クーポン自動配信

- **タイミング**: 毎日 **09:00 JST** に自動実行
- **対象**: 誕生日が今日 かつ 友だち登録済み かつ 今年未送信のユーザー
- **内容**: 「乾杯ドリンク1杯プレゼント」クーポン（Flexメッセージ）

### 誕生日登録フロー
1. リッチメニュー「④ 誕生日登録」をタップ
2. 登録案内メッセージが届く
3. 「誕生日 3月15日」の形式でメッセージ送信
4. 登録完了メッセージが届く

---

## 将来の拡張計画

- [ ] セグメント配信（常連/新規/久しぶり）
- [ ] 予約リンク連携（ネット予約サービスへ誘導）
- [ ] 来店回数に応じたランク制（ブロンズ/シルバー/ゴールド）
- [ ] LINE LIFFを使った誕生日登録フォーム（UX向上）
- [ ] PostgreSQLへの移行（本番スケール対応）
- [ ] 管理ダッシュボード（KPI可視化）

---

## 関連ドキュメント

- [LINE Developers 設定手順](./docs/line-developers-setup.md)
- [ショップカード設定手順](./docs/shop-card-setup.md)
- [メッセージ配信テンプレート集](./docs/message-templates.md)

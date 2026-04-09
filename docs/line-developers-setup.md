# LINE Developers 設定手順書
## お肉膳スギモト 三井アウトレットパーク岡崎店

---

## STEP 1: LINE Developers アカウント作成

1. [LINE Developers](https://developers.line.biz/ja/) にアクセス
2. 右上「コンソールへのログイン」をクリック
3. 個人LINEアカウントでログイン（テスト用は個人アカウントでOK）

---

## STEP 2: プロバイダー作成

1. コンソール上部「新規プロバイダー作成」をクリック
2. プロバイダー名を入力（例：`スギモト飲食グループ`）
3. 「作成」をクリック

---

## STEP 3: Messaging APIチャネル作成

1. プロバイダーページで「新規チャネル作成」→「Messaging API」を選択
2. 以下を入力：

| 項目 | 入力値 |
|------|--------|
| チャネルの種類 | Messaging API |
| プロバイダー | （作成したもの） |
| チャネルアイコン | 店舗ロゴ画像 |
| チャネル名 | お肉膳スギモト 岡崎店 |
| チャネル説明 | 三井アウトレットパーク岡崎店 公式LINE |
| 大業種 | 飲食店・レストラン |
| 小業種 | 焼肉・ホルモン |
| メールアドレス | 担当者メールアドレス |

3. 利用規約に同意して「作成」

---

## STEP 4: チャネルシークレット・アクセストークン取得

### チャネルシークレット
1. チャネル設定 → 「チャネル基本設定」タブ
2. 「チャネルシークレット」をコピー
3. `.env` の `LINE_CHANNEL_SECRET` に貼り付け

### チャネルアクセストークン（長期）
1. チャネル設定 → 「Messaging API設定」タブ
2. 一番下「チャネルアクセストークン（長期）」
3. 「発行」ボタンをクリック
4. 表示されたトークンをコピー
5. `.env` の `LINE_CHANNEL_ACCESS_TOKEN` に貼り付け

```env
LINE_CHANNEL_SECRET=abcdef1234567890abcdef1234567890
LINE_CHANNEL_ACCESS_TOKEN=eyJhbGciOi...（長いトークン）
```

---

## STEP 5: Webhook URL の設定

### アプリをデプロイ後（Renderの場合）
1. Renderでデプロイ完了後、URLを取得（例：`https://sugimoto-line-bot.onrender.com`）

### LINE Developersでの設定
1. 「Messaging API設定」タブ → 「Webhook設定」
2. Webhook URL に以下を入力：
   ```
   https://sugimoto-line-bot.onrender.com/callback
   ```
3. 「更新」→「検証」をクリック
4. 「成功」と表示されればOK ✅
5. 「Webhookの利用」を **オン** にする

---

## STEP 6: 自動応答メッセージの無効化

LINE Official Account Manager での設定が必要です。

1. [LINE Official Account Manager](https://manager.line.biz/) にログイン
2. 対象アカウントを選択
3. 左メニュー「応答設定」
4. 以下の設定に変更：

| 設定項目 | 値 |
|---------|-----|
| 応答モード | **Bot** |
| Webhook | **オン** |
| 応答メッセージ | **オフ**（Botが返すため） |
| あいさつメッセージ | **オフ**（Botのウェルカムメッセージを使用） |

> ⚠️ 「応答メッセージ」をオンのままにすると、自動応答とBotの両方が返信して二重になります

---

## STEP 7: 友だちQRコードの確認

1. LINE Official Account Manager → 「友だちを増やす」
2. QRコードをダウンロード → 店頭POPやメニューに掲載

---

## STEP 8: 動作確認

1. スマホでLINEを開き、作成したボットアカウントを友だち追加
2. ウェルカムメッセージ + クーポンが届くか確認
3. リッチメニューのボタンをタップして動作確認

---

## トラブルシューティング

### Webhook検証が失敗する
- アプリが起動しているか確認（`/health` エンドポイントにアクセス）
- URLの末尾に `/callback` がついているか確認
- HTTPSであることを確認（HTTP不可）

### メッセージが来ない
- 「Webhookの利用」がオンになっているか確認
- サーバーのログでエラーが出ていないか確認
- チャネルアクセストークンが正しいか確認

### 署名検証エラー
- `LINE_CHANNEL_SECRET` が正しいか確認
- チャネルシークレットとアクセストークンが同じチャネルのものか確認

# 004_events_pagination_fix

## 対応対象
- `src/calendar_client.py`

## 問題
- `get_events()` / `get_today_events()` で `nextPageToken` を追跡せず、1ページ目しか取得しない。

## 修正方針（どう直すか）
- イベント取得処理を共通化し、全取得系メソッドでページネーションを必須化する。
- `timeMin/timeMax`、`calendarId`、`singleEvents/orderBy` の指定を共通関数へ集約。

## 実装タスク
- [ ] `events().list(...).execute()` のループ共通関数を追加
- [ ] `get_events/get_today_events/_get_events_from_service` を共通関数利用に変更
- [ ] 既存ソート/フィルタの整合性を維持

## 受け入れ条件
- [ ] 2ページ以上あるカレンダーでも全件取得される
- [ ] today/week 両方の取得件数が欠落しない

## テスト観点
- [ ] `nextPageToken` あり/なしケース
- [ ] 複数カレンダー + ページネーション併用ケース

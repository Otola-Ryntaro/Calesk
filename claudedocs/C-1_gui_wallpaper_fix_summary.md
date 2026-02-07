# C-1修正完了レポート: GUIの壁紙生成とカレンダー取得統合

**作業日**: 2026-02-05
**優先度**: CRITICAL
**ステータス**: ✅ 完了

## 🎯 解決した問題

### C-1: GUIの壁紙生成が必ず失敗する
- **症状**: GUI経由の壁紙更新で `ImageGenerator.generate()` が呼ばれるが実装がない
- **根本原因**: WallpaperServiceが存在しないメソッド`generate()`を呼び出し、引数も不一致

### H-1: GUI更新フローでカレンダー取得がない
- **症状**: GUI更新時にイベント取得が走らず、常に空データで描画される
- **根本原因**: WallpaperServiceにCalendarClientが統合されていない

### M-3: API設計不一致
- **症状**: `ImageGenerator.generate_wallpaper()` は today/week を要求、Service層は単一リスト前提
- **根本原因**: GUIとCLIで異なるAPI設計

## ✅ 実施した修正

### 1. WallpaperService修正

**変更内容:**
- `CalendarClient`を統合してイベント取得機能を追加
- API統一: `generate()` → `generate_wallpaper(today_events, week_events)`
- `events`引数を削除（内部でCalendarClient使用）

**修正ファイル:**
- [src/viewmodels/wallpaper_service.py](../src/viewmodels/wallpaper_service.py)

**主な変更:**
```python
# Before
def generate_wallpaper(self, theme_name: str, events: List[Dict], output_path: Optional[Path] = None) -> Path:
    image_path = self.image_generator.generate(events, output_path)

# After
def generate_wallpaper(self, theme_name: str) -> Path:
    # Google Calendar認証
    if not self.calendar_client.authenticate():
        raise Exception("Google Calendar API認証に失敗しました")

    # イベント取得
    today_events = self.calendar_client.get_today_events()
    week_events = self.calendar_client.get_week_events()

    # 壁紙生成
    image_path = self.image_generator.generate_wallpaper(today_events, week_events)
```

### 2. MainViewModel修正

**変更内容:**
- `update_wallpaper(events)` → `update_wallpaper()`: events引数を削除
- `generate_preview(events)` → `generate_preview()`: events引数を削除
- WallpaperWorkerの初期化からevents削除

**修正ファイル:**
- [src/viewmodels/main_viewmodel.py](../src/viewmodels/main_viewmodel.py)

### 3. WallpaperWorker修正

**変更内容:**
- `__init__(service, theme, events)` → `__init__(service, theme)`: events引数を削除

**修正ファイル:**
- [src/viewmodels/wallpaper_worker.py](../src/viewmodels/wallpaper_worker.py)

### 4. テスト修正

**変更内容:**
- WallpaperServiceテスト: CalendarClientのモック追加、APIテスト更新
- WallpaperWorkerテスト: events引数削除
- MainViewModelテスト: events関連テスト削除（WallpaperServiceでテスト）

**修正ファイル:**
- [tests/test_wallpaper_service.py](../tests/test_wallpaper_service.py): 3テスト追加（認証失敗、実データ）
- [tests/test_wallpaper_worker.py](../tests/test_wallpaper_worker.py): events引数削除
- [tests/test_main_viewmodel.py](../tests/test_main_viewmodel.py): events関連テスト削除

## 📊 テスト結果

**全テスト合格**: ✅ **34テスト**

### テスト内訳

| テストファイル | テスト数 | 結果 |
|---------------|---------|------|
| test_wallpaper_service.py | 9 | ✅ 全合格 |
| test_wallpaper_worker.py | 8 | ✅ 全合格 |
| test_main_viewmodel.py | 17 | ✅ 全合格 |

**実行時間**: 7.08秒

### 新規追加テスト

**WallpaperService:**
1. `test_generate_wallpaper_authentication_failure`: CalendarClient認証失敗時の処理
2. `test_generate_wallpaper_with_events`: 実際のイベントデータで壁紙生成

**WallpaperWorker:**
- `test_wallpaper_worker_with_different_theme`: 異なるテーマでの動作確認

## 🎯 解決された問題

### ✅ C-1: GUIの壁紙生成が動作する
- WallpaperServiceが正しいAPI（`generate_wallpaper()`）を呼び出し
- 引数が正しく渡される（today_events, week_events）

### ✅ H-1: GUIでGoogle Calendarから実データを取得
- WallpaperServiceが内部でCalendarClientを使用
- 認証→イベント取得→壁紙生成のフロー確立

### ✅ M-3: API設計が統一された
- GUI/CLIで同じAPI: `generate_wallpaper(today_events, week_events)`
- Service層でイベント取得を担当（責務の明確化）

## 🔍 動作フロー（修正後）

```
[ユーザー]
    ↓ 「壁紙を更新」ボタンクリック
[MainWindow]
    ↓ update_wallpaper()
[MainViewModel]
    ↓ WallpaperWorker作成（theme_nameのみ）
[WallpaperWorker]
    ↓ generate_and_set_wallpaper(theme_name)
[WallpaperService]
    ↓ CalendarClient.authenticate()
    ↓ get_today_events() / get_week_events()
    ↓ ImageGenerator.generate_wallpaper(today, week)
[ImageGenerator]
    ↓ 壁紙画像生成
[WallpaperSetter]
    ↓ 壁紙設定
[完了]
```

## 📝 設計の改善点

### Before（問題あり）
- GUIとCLIで異なるAPI設計
- WallpaperServiceがイベント取得を行わない
- 外部からevents引数を渡す設計

### After（改善後）
- **単一責務の原則**: WallpaperServiceがカレンダー取得を担当
- **API統一**: GUI/CLIで同じフロー
- **疎結合**: ViewModelはイベント取得の詳細を知らない
- **テスタビリティ**: CalendarClientをモック可能

## 🚀 今後の課題

### 残っている問題（High優先度）

**H-2: イベントスキーマの統一**
- 現状: `start` (文字列) vs `start_datetime` (datetime)
- 対応: 統一Eventモデル（dataclass）の作成

**H-3: 「今日の予定」ロジックの修正**
- 現状: `timeMin=now` のため既開始イベントが落ちる
- 対応: 00:00-23:59の範囲指定

### Medium/Low優先度
- M-1: 通知重複防止
- M-2: 週間カレンダー重複表示改善
- L-1/L-2: 設定コメント整合性、Pillow内部属性アクセス

## 📋 関連ドキュメント

- チケット: [docs/009_gui_core_implementation_fixes.md](../docs/009_gui_core_implementation_fixes.md)
- Codexレビュー: [Codex/review_notes.md](../Codex/review_notes.md)
- アーキテクチャ: [docs/architecture.md](../docs/architecture.md)

---

**完了日**: 2026-02-05
**ステータス**: ✅ C-1/H-1/M-3 完全解決

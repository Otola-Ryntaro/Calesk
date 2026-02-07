# チケット020: 背景画像アップロード機能

## 概要

GUIから壁紙の背景画像をユーザーがアップロード（選択）できるようにする。
選択した画像をカレンダー壁紙の背景として使用する。

## 要件

### 機能
- GUIで「背景画像を選択」ボタンを提供
- ファイルダイアログで画像ファイル（PNG/JPG/JPEG）を選択
- 選択した画像を背景としてプレビューに反映
- 「デフォルトに戻す」ボタンで初期背景に復帰
- 選択した画像パスはconfig/設定として保持

### UI
- 背景画像選択ボタン（コントロールエリアに追加）
- 現在の背景画像ファイル名をラベル表示
- 「デフォルト背景に戻す」ボタン

### 技術的要件
- 画像のリサイズ処理（壁紙サイズに合わせる）
- 対応フォーマット: PNG, JPG, JPEG
- 選択した画像パスの永続化（config.py の BACKGROUND_IMAGE_PATH と連携）

## タスク

### ViewModel層
- [x] `MainViewModel.set_background_image()` メソッド追加（バリデーション付き）
- [x] `MainViewModel.reset_background_image()` メソッド追加
- [x] `background_image_changed` シグナル追加
- [x] 背景画像パスの状態管理（`background_image_path` プロパティ）

### View層
- [x] 「背景画像を選択」ボタン追加
- [x] QFileDialogによる画像ファイル選択
- [x] 背景画像ファイル名ラベル表示
- [x] 「デフォルトに戻す」ボタン追加

### Service層
- [x] `WallpaperService` に背景画像パス設定の対応
- [x] `ImageGenerator` に背景画像パスの動的変更対応

### テスト
- [x] ViewModel の背景画像関連メソッドのテスト
- [x] 画像パスの検証テスト（存在確認、拡張子、ファイルサイズ）
- [x] デフォルト復帰テスト

## 変更ファイル

- `src/viewmodels/main_viewmodel.py` - 背景画像管理メソッド追加
- `src/ui/main_window.py` - ファイル選択UI追加
- `src/viewmodels/wallpaper_service.py` - 背景画像パス対応
- `src/image_generator.py` - 背景画像動的変更対応
- `tests/test_background_upload.py` - 新規テスト

## 優先度: MEDIUM
## 工数: 中（3-4時間）

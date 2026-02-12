# 027: Dock制御（ウィンドウ表示中のみDock表示）

## 概要

macOSでアプリ起動時にDockに「Python」として表示される問題を修正する。
メニューバー常駐時はDock非表示、ウィンドウ表示中のみDockに表示する。

## アプリ名

**Calesk（カレスク）** — calendar + desk の造語

## 現状

- Dock にデフォルトの Python アイコンが表示される
- メニューバーのトレイアイコンは `SP_ComputerIcon`（システムデフォルト）
- ウィンドウ閉じ時はメニューバーに格納済み（closeEvent で hide）

## タスク

### Phase 1: Dock制御

- [ ] ウィンドウ非表示時: `NSApplication.setActivationPolicy_(Accessory)` でDock非表示
- [ ] ウィンドウ表示時: `NSApplication.setActivationPolicy_(Regular)` でDock表示
- [ ] `_show_window()` / `closeEvent()` にポリシー切り替えを追加
- [ ] ビルド時: spec ファイルの Info.plist に `LSUIElement = True` を追加
- [ ] Dock表示/非表示の切り替えが正常に動作することを確認

### Phase 2: トレイアイコン適用

- [ ] メニューバーのトレイアイコンにカスタムアイコンを適用（`assets/tray_icon.png`）
- [ ] 現在の `SP_ComputerIcon` を置き換え

### 注意事項

- `Accessory` モードでは Cmd+Tab に表示されない（メニューバーから操作）
- `Regular` に戻すとウィンドウ操作中は通常のアプリと同じ挙動になる

# 003: Google Calendar アイコン統合

## 優先度
**MEDIUM**

## 要件
- [ ] Macの場合: 上部ヘッダーにアイコン配置
- [ ] Windowsの場合: 右下フッターにアイコン配置
- [ ] アイコンクリックでGoogle Calendarをブラウザで開く

## 技術仕様

### アイコン配置
- Mac: 画像上部（Y: 10-30px）、右寄せ（X: IMAGE_WIDTH - 60px）
- Windows: 画像下部（Y: IMAGE_HEIGHT - 60px）、右寄せ（X: IMAGE_WIDTH - 60px）
- アイコンサイズ: 40x40px

### アイコン実装方法
**Option 1: 壁紙にアイコンを描画（推奨）**
- Google Calendarアイコン画像を用意
- Pillowで壁紙に重ねて描画
- クリック可能領域は別途対応が必要

**Option 2: 壁紙とは別にGUIアイコン配置**
- tkinterやPyQt5でデスクトップアイコンを配置
- クリック時のイベントハンドリングが容易
- OSごとに実装が異なる

**推奨アプローチ: Option 1（壁紙描画）**
- 理由: シンプル、OS依存が少ない
- クリック機能は将来的な拡張として検討

### Google Calendar URL
```python
GOOGLE_CALENDAR_URL = "https://calendar.google.com"
```

## 影響範囲
- `src/image_generator.py`: アイコン描画メソッド追加
- `src/config.py`: アイコン設定追加
- 新規ファイル: `assets/google_calendar_icon.png`

## タスク
- [ ] Google Calendarアイコン画像を用意（40x40px、PNG）
- [ ] `_draw_calendar_icon()` メソッド実装
- [ ] OS判定に基づいて配置位置を変更
- [ ] （将来）クリック機能の検討

## テスト観点
- [ ] Macで上部にアイコンが表示される
- [ ] Windowsで右下にアイコンが表示される
- [ ] アイコンが適切なサイズで表示される
- [ ] 他の要素と重ならない

## 備考
- 壁紙上のアイコンクリックは技術的に困難（壁紙は静的画像）
- クリック機能が必要な場合は、別途デスクトップアプリケーション化が必要
- 現時点では視覚的な表示のみを実装

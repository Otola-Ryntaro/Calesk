# Setup Check

プロジェクトの開発環境が正しく設定されているか確認する。

## チェック項目

以下を順番に確認し、結果を報告:

1. **Git**: `git status` でリポジトリ状態を確認
2. **CLAUDE.md**: プロジェクトルートにCLAUDE.mdが存在するか
3. **Hooks**: `.claude/settings.json` が存在し、フックが設定されているか
4. **Codex MCP**: `mcp__codex-cli__ping` が利用可能か（pingを送信）
5. **Harness**: Plans.md等のSSOTファイルの状態
6. **依存パッケージ**: requirements.txt / venv が存在するか
7. **テスト**: テストファイルが存在し、実行可能か

結果を表形式でまとめること。問題があれば修正方法も提示する。

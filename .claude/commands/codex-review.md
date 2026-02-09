# Codex Code Review

Codex MCPを使用して、現在の変更に対するセカンドオピニオンレビューを実行する。

## 手順

1. `mcp__codex-cli__review` を以下のパラメータで実行:
   - uncommitted: true
   - prompt: "以下の観点でレビューしてください: 1) セキュリティ脆弱性 2) パフォーマンスの問題 3) コードの保守性 4) エッジケースの見落とし。日本語で回答してください。"

2. Codexの結果を受け取ったら、自身の分析と比較して以下を報告:
   - Codexと自分の分析が一致している点
   - 意見が異なる点とその理由
   - 総合的な推奨事項

3. MCP接続エラーの場合、Bash経由でフォールバック:
   ```bash
   codex exec --output-last-message /tmp/claude/review.txt "Review uncommitted changes. Focus on security, performance, maintainability. Reply in Japanese."
   cat /tmp/claude/review.txt
   ```

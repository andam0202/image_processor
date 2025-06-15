# Image Processor Makefile
# Python 3.12+ プロジェクト用の開発タスク

.PHONY: help setup install clean format lint typecheck test test-unit test-property test-integration test-cov benchmark profile security audit check check-all pr issue

# デフォルトターゲット
help: ## このヘルプメッセージを表示
	@echo "Image Processor - 開発用Makefileコマンド"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# 基本セットアップ
setup: ## 開発環境をセットアップ
	@echo "🔧 開発環境をセットアップ中..."
	uv sync --all-extras
	uv run pre-commit install
	@echo "✅ セットアップ完了"

install: ## 依存関係をインストール
	@echo "📦 依存関係をインストール中..."
	uv sync

# コード品質
format: ## コードをフォーマット
	@echo "🎨 コードフォーマット中..."
	uv run ruff format src/ tests/

lint: ## リントチェック（自動修正付き）
	@echo "🔍 リントチェック中..."
	uv run ruff check src/ tests/ --fix

typecheck: ## 型チェック（strict mode）
	@echo "🔬 型チェック中..."
	uv run mypy src/ --strict

# テスト関連
test: ## 全テスト実行
	@echo "🧪 全テスト実行中..."
	uv run pytest tests/

test-unit: ## 単体テストのみ実行
	@echo "🧪 単体テスト実行中..."
	uv run pytest tests/unit/ -v

test-property: ## プロパティベーステストのみ実行
	@echo "🧪 プロパティベーステスト実行中..."
	uv run pytest tests/property/ -v

test-integration: ## 統合テストのみ実行
	@echo "🧪 統合テスト実行中..."
	uv run pytest tests/integration/ -v

test-cov: ## カバレッジ付きテスト実行
	@echo "🧪 カバレッジ付きテスト実行中..."
	uv run pytest tests/ --cov=src --cov-report=html --cov-report=term

# パフォーマンス測定
benchmark: ## ローカルベンチマーク実行
	@echo "⚡ ベンチマーク実行中..."
	uv run pytest tests/ -k "benchmark" --benchmark-only

profile: ## プロファイリング実行
	@echo "📊 プロファイリング実行中..."
	uv run python -m cProfile -o profile.stats -m pytest tests/unit/
	@echo "profile.stats に結果を保存しました"

# セキュリティ
security: ## セキュリティチェック
	@echo "🔒 セキュリティチェック中..."
	uv run bandit -r src/ -f json -o security-report.json
	uv run bandit -r src/ 

audit: ## 依存関係の脆弱性チェック
	@echo "🔍 依存関係の脆弱性チェック中..."
	uv run pip-audit

# 統合チェック
check: ## format, lint, typecheck, test を順番に実行
	@echo "🔄 統合チェック実行中..."
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) test

check-all: ## pre-commit で全ファイルをチェック
	@echo "🔄 全ファイルチェック中..."
	uv run pre-commit run --all-files

# GitHub操作
pr: ## プルリクエストを作成 (TITLE, BODY, LABEL オプション)
	@if [ -z "$(TITLE)" ]; then \
		echo "❌ エラー: TITLE を指定してください"; \
		echo "使用例: make pr TITLE=\"機能追加\" BODY=\"新機能を実装\" LABEL=\"enhancement\""; \
		exit 1; \
	fi
	@BODY_ARG=""; \
	if [ -n "$(BODY)" ]; then \
		BODY_ARG="--body \"$(BODY)\""; \
	fi; \
	LABEL_ARG=""; \
	if [ -n "$(LABEL)" ]; then \
		LABEL_ARG="--label \"$(LABEL)\""; \
	fi; \
	echo "📤 プルリクエスト作成中: $(TITLE)"; \
	eval "gh pr create --title \"$(TITLE)\" $$BODY_ARG $$LABEL_ARG"

issue: ## イシューを作成 (TITLE, BODY, LABEL オプション)
	@if [ -z "$(TITLE)" ]; then \
		echo "❌ エラー: TITLE を指定してください"; \
		echo "使用例: make issue TITLE=\"バグ報告\" BODY=\"エラーの詳細\" LABEL=\"bug\""; \
		exit 1; \
	fi
	@BODY_ARG=""; \
	if [ -n "$(BODY)" ]; then \
		BODY_ARG="--body \"$(BODY)\""; \
	fi; \
	LABEL_ARG=""; \
	if [ -n "$(LABEL)" ]; then \
		LABEL_ARG="--label \"$(LABEL)\""; \
	fi; \
	echo "📝 イシュー作成中: $(TITLE)"; \
	eval "gh issue create --title \"$(TITLE)\" $$BODY_ARG $$LABEL_ARG"

# クリーンアップ
clean: ## キャッシュファイルを削除
	@echo "🧹 クリーンアップ中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -f profile.stats security-report.json
	@echo "✅ クリーンアップ完了"

# 開発用ユーティリティ
dev-install: ## 開発モードでインストール
	@echo "🔧 開発モードでインストール中..."
	uv pip install -e .

build: ## パッケージをビルド
	@echo "📦 パッケージビルド中..."
	uv build

publish-test: ## TestPyPIにパッケージを公開
	@echo "📤 TestPyPIにパッケージ公開中..."
	uv publish --repository testpypi

publish: ## PyPIにパッケージを公開
	@echo "📤 PyPIにパッケージ公開中..."
	uv publish

# 便利なエイリアス
fmt: format ## format のエイリアス
test-fast: test-unit ## 高速テスト（単体テストのみ）
test-slow: test-integration ## 低速テスト（統合テスト）
cov: test-cov ## カバレッジのエイリアス
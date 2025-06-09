# Image Processor

娯楽用動画・画像素材加工のためのツール群

## 概要

このプロジェクトは、動画や画像の素材を効率的に加工するためのPythonツール集です。
主に以下の機能を提供します：

- **画像フォーマット変換**: DDS, JPG, WebP, PNG間の変換
- **背景透過処理**: AI技術を使った自動背景除去
- **4コマ漫画分割**: 漫画画像の自動コマ分割
- **動画処理**: フレーム抽出、時間分割
- **ファイル管理**: 一括リネーム、整理

## クイックスタート

1. **依存関係のインストール**:
   ```bash
   pip install pillow rembg tqdm wand
   ```

2. **システム依存関係**:
   ```bash
   # Ubuntu/Debian
   sudo apt install imagemagick ffmpeg
   ```

3. **基本的な使用例**:
   ```bash
   # 画像を data/input に配置して背景透過処理
   python tools/image_processing/remove_img.py
   
   # JPGファイルをPNGに変換
   python tools/image_conversion/format_converter.py -f png
   ```

## ディレクトリ構造

```
image_processor/
├── data/
│   ├── input/              # 入力ファイル
│   └── output/             # 出力ファイル
├── tools/
│   ├── common.py           # 共通処理ライブラリ
│   ├── image_conversion/   # 画像フォーマット変換
│   │   ├── dds2png.py
│   │   └── format_converter.py
│   ├── image_processing/   # 画像処理・加工
│   │   ├── remove_img.py
│   │   └── koma_separator.py
│   ├── video_processing/   # 動画処理
│   │   ├── video2koma.py
│   │   └── video_divider.py
│   └── utilities/          # ユーティリティ
│       ├── rename.py
│       └── prompts.md
├── julia/                  # Julia実験用
└── USAGE.md               # 詳細使用方法
```

## 主要機能

### 🖼️ 画像処理
- **背景透過**: AI技術による自動背景除去（アニメ画像に特化）
- **フォーマット変換**: JPG/PNG/WebP/DDS間の相互変換
- **4コマ分割**: 学マス4コマ漫画の自動分割

### 🎬 動画処理  
- **フレーム抽出**: 指定間隔でのフレーム抽出
- **動画分割**: 時間指定での動画分割
- **背景透過動画**: 動画フレームの背景透過処理

### 🔧 ユーティリティ
- **ファイルリネーム**: 連番、パターン、ゼロパディング
- **バッチ処理**: 複数ファイルの一括処理

## 詳細な使用方法

詳しい使い方は [USAGE.md](USAGE.md) をご覧ください。

## 開発環境

### 推奨: 仮想環境 (venv)

```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows

# 依存パッケージのインストール
pip install pillow rembg tqdm wand

# 仮想環境の無効化
deactivate
```

### 代替: uv (高速パッケージマネージャー)

```bash
# uvのインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクト初期化
uv init

# パッケージの追加
uv add pillow rembg tqdm wand

# 実行
uv run tools/image_processing/remove_img.py
```

**注意**: rembgが一部環境でuvと互換性がない場合があります。

## 必要な外部ツール

- **ImageMagick**: DDSファイル変換用
- **FFmpeg**: 動画処理用

## ライセンス

個人利用目的のツールです。

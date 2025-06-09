# Image Processor Tools - 使用方法

## 概要

動画・画像素材の加工を効率的に行うためのツール群です。整理された構造で使いやすくなっています。

## ディレクトリ構造

```
image_processor/
├── data/
│   ├── input/          # 入力ファイル用
│   └── output/         # 出力ファイル用
├── tools/
│   ├── common.py       # 共通処理
│   ├── image_conversion/   # 画像フォーマット変換
│   ├── image_processing/   # 画像処理
│   ├── video_processing/   # 動画処理
│   └── utilities/          # ユーティリティ
└── julia/              # Julia実験用
```

## 基本的な使い方

すべてのツールは共通のインターフェースを持っています：

- `-i, --input`: 入力ディレクトリ（デフォルト: data/input）
- `-o, --output`: 出力ディレクトリ（デフォルト: data/output）
- `-v, --verbose`: 詳細な出力表示
- `-h, --help`: ヘルプ表示

## ツール詳細

### 1. 画像フォーマット変換 (image_conversion)

#### format_converter.py - 汎用画像フォーマット変換
様々な画像フォーマット間の変換を行います。

```bash
# PNG形式に変換
python tools/image_conversion/format_converter.py -f png

# JPEG形式に変換（元ファイル保持）
python tools/image_conversion/format_converter.py -f jpg --keep-original

# 特定の拡張子のみ処理
python tools/image_conversion/format_converter.py -f png --extensions .webp .tiff
```

**サポートフォーマット**: JPG, PNG, WebP

#### dds2png.py - DDS専用変換
DDSファイルをPNG形式に変換します。

```bash
# 基本変換
python tools/image_conversion/dds2png.py

# 元ファイル保持
python tools/image_conversion/dds2png.py --keep-original
```

**依存関係**: `pip install Wand` + ImageMagickのシステムインストール

### 2. 画像処理 (image_processing)

#### remove_img.py - 背景透過処理
AI を使用して画像・動画の背景を透過処理します。

```bash
# 基本的な背景透過（アニメ特化モデル）
python tools/image_processing/remove_img.py

# 汎用モデルを使用
python tools/image_processing/remove_img.py -m isnet-general-use

# 出力ディレクトリをクリア
python tools/image_processing/remove_img.py --clear-output

# 動画処理（30fps）
python tools/image_processing/remove_img.py --fps 30
```

**利用可能モデル**:
- `isnet-anime`: アニメ画像特化（デフォルト）
- `isnet-general-use`: 汎用
- `birefnet-general`: 高精度汎用
- `birefnet-general-lite`: 軽量版

**依存関係**: `pip install rembg pillow tqdm`

#### koma_separator.py - 4コマ漫画分割
4コマ漫画を各コマに分割します。

```bash
# 学マス仕様（デフォルト）で分割
python tools/image_processing/koma_separator.py

# カスタム座標で分割
python tools/image_processing/koma_separator.py --coordinates "100,200,800,700;100,800,800,1300;..."

# PNG形式で出力
python tools/image_processing/koma_separator.py --format png --quality 100
```

**座標フォーマット**: `x1,y1,x2,y2;x1,y1,x2,y2;...`

### 3. 動画処理 (video_processing)

#### video2koma.py - フレーム抽出
動画から一定間隔でフレームを抽出します。

```bash
# 1秒間隔でフレーム抽出
python tools/video_processing/video2koma.py -n 1

# 高品質JPEGで3秒間隔
python tools/video_processing/video2koma.py -n 3 -q 1 -f jpg

# PNG形式で出力
python tools/video_processing/video2koma.py -f png
```

**品質設定**: 1（最高品質）〜31（最低品質）

#### video_divider.py - 動画分割
動画を一定時間ごとに分割します。

```bash
# 30分ごとに分割
python tools/video_processing/video_divider.py -m 30

# 10分ごとに分割
python tools/video_processing/video_divider.py -m 10
```

**依存関係**: FFmpegのシステムインストールが必要

### 4. ユーティリティ (utilities)

#### rename.py - ファイル名一括変更
ファイル名の一括変更を行います。

```bash
# 連番リネーム
python tools/utilities/rename.py sequential -p "gakumasu4koma" -s 0 -z 4
# 結果: gakumasu4koma_0000.jpg, gakumasu4koma_0001.jpg, ...

# 正規表現パターンでリネーム
python tools/utilities/rename.py pattern -p "img_comics_(\d+)" -r "comic_\1"
# 結果: img_comics_01.jpg -> comic_01.jpg

# 数字部分をゼロパディング
python tools/utilities/rename.py padding -p 4
# 結果: file_1.jpg -> file_0001.jpg
```

**サブコマンド**:
- `sequential`: 連番リネーム
- `pattern`: 正規表現パターンリネーム  
- `padding`: ゼロパディング

## 開発環境セットアップ

### 仮想環境（推奨）

```bash
# 仮想環境作成
python3 -m venv venv

# 有効化（Linux/Mac）
source venv/bin/activate

# 有効化（Windows）
venv\Scripts\activate

# 必要パッケージインストール
pip install pillow rembg tqdm wand
```

### システム依存関係

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install imagemagick ffmpeg

# macOS (Homebrew)
brew install imagemagick ffmpeg

# Windows
# FFmpeg: https://ffmpeg.org/download.html
# ImageMagick: https://imagemagick.org/script/download.php
```

## 使用例

### よくあるワークフロー

1. **4コマ漫画の処理**:
   ```bash
   # 1. 画像をdata/inputに配置
   # 2. 4コマに分割
   python tools/image_processing/koma_separator.py
   # 3. 背景透過処理
   python tools/image_processing/remove_img.py -i data/output -o data/final
   ```

2. **動画からの素材抽出**:
   ```bash
   # 1. 動画をdata/inputに配置
   # 2. フレーム抽出
   python tools/video_processing/video2koma.py -n 2
   # 3. 背景透過処理
   python tools/image_processing/remove_img.py -i data/output -o data/final
   ```

3. **ファイル整理**:
   ```bash
   # 1. フォーマット統一
   python tools/image_conversion/format_converter.py -f png
   # 2. ファイル名整理
   python tools/utilities/rename.py sequential -p "processed" -s 1
   ```

## トラブルシューティング

### エラー対処

**ImportError (Wand)**: 
```bash
pip install Wand
# Ubuntu: sudo apt install imagemagick
```

**ImportError (rembg)**:
```bash
pip install rembg
```

**FFmpeg not found**:
```bash
# Ubuntu: sudo apt install ffmpeg
# Windows: 公式サイトからダウンロード
```

### ログ確認

すべてのツールは詳細なログを出力します：
```bash
python tools/xxx/xxx.py -v  # 詳細ログ表示
```

## 注意事項

- 処理前に必ずバックアップを取ってください
- 大きなファイル・大量のファイル処理には時間がかかります
- 背景透過処理は初回実行時にモデルをダウンロードします（数GB）

## ライセンス・免責事項

個人利用目的のツールです。商用利用時は各種ライブラリのライセンスを確認してください。
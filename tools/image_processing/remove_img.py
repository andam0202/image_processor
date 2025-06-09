#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像・動画の背景透過処理ツール
依存関係: pip install rembg pillow tqdm
"""

import sys
import logging
import subprocess
from pathlib import Path
from PIL import Image
from tqdm import tqdm

try:
    from rembg import remove, new_session
except ImportError:
    print("Error: rembgライブラリがインストールされていません。")
    print("pip install rembg を実行してインストールしてください。")
    sys.exit(1)

# 親ディレクトリのcommon.pyをインポート
sys.path.append(str(Path(__file__).parent.parent))
from common import setup_logging, create_base_parser, validate_directories, get_files_by_extension

def remove_background_from_image(input_file: Path, output_dir: str, session) -> bool:
    """画像の背景を透過処理"""
    try:
        with Image.open(input_file) as img:
            # RGBA形式に変換
            img = img.convert("RGBA")
            processed_img = remove(img, session=session)
            
            output_path = Path(output_dir) / input_file.name
            processed_img.save(output_path)
            
            logging.info(f"背景透過完了: {input_file.name}")
            return True
            
    except Exception as e:
        logging.error(f"背景透過エラー {input_file.name}: {e}")
        return False

def process_video_frames(input_file: Path, output_dir: str, session, fps: int = 30) -> bool:
    """動画のフレームを抽出し背景透過処理"""
    try:
        temp_dir = Path(output_dir) / "temp_frames"
        temp_dir.mkdir(exist_ok=True)
        
        # フレーム抽出
        frame_pattern = str(temp_dir / f"{input_file.stem}_%04d.png")
        cmd = [
            "ffmpeg", "-i", str(input_file),
            "-vf", f"fps={fps}",
            "-y", frame_pattern
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"フレーム抽出エラー: {result.stderr}")
            return False
        
        # 抽出されたフレームを処理
        frame_files = list(temp_dir.glob(f"{input_file.stem}_*.png"))
        if not frame_files:
            logging.error("フレームが抽出されませんでした")
            return False
        
        logging.info(f"{len(frame_files)}フレームを背景透過処理中...")
        
        for frame_file in tqdm(frame_files, desc="フレーム処理"):
            remove_background_from_image(frame_file, str(temp_dir), session)
        
        # 透過処理済みフレームを動画に再合成
        output_video = Path(output_dir) / f"{input_file.stem}_transparent.mp4"
        cmd = [
            "ffmpeg", "-r", "30",
            "-i", str(temp_dir / f"{input_file.stem}_%04d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-y", str(output_video)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 一時ファイルの削除
        for frame_file in temp_dir.glob("*.png"):
            frame_file.unlink()
        temp_dir.rmdir()
        
        if result.returncode == 0:
            logging.info(f"動画透過処理完了: {output_video.name}")
            return True
        else:
            logging.error(f"動画合成エラー: {result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"動画処理エラー {input_file.name}: {e}")
        return False

def main():
    parser = create_base_parser("画像・動画の背景透過処理")
    parser.add_argument('-m', '--model',
                       choices=['isnet-general-use', 'isnet-anime', 'birefnet-general', 'birefnet-general-lite'],
                       default='isnet-anime',
                       help='使用するrembgモデル (デフォルト: isnet-anime)')
    parser.add_argument('--fps', type=int, default=30,
                       help='動画処理時のFPS (デフォルト: 30)')
    parser.add_argument('--clear-output', action='store_true',
                       help='処理前に出力ディレクトリを空にする')
    args = parser.parse_args()
    
    setup_logging()
    
    if not validate_directories(args.input, args.output):
        sys.exit(1)
    
    # 出力ディレクトリをクリア
    if args.clear_output:
        output_path = Path(args.output)
        for file in output_path.glob("*"):
            if file.is_file():
                file.unlink()
    
    # rembgセッション初期化
    session = new_session(args.model)
    logging.info(f"rembgモデル '{args.model}' を使用します")
    
    # 画像ファイルの処理
    image_files = get_files_by_extension(args.input, ['.jpg', '.jpeg', '.png', '.webp'])
    video_files = get_files_by_extension(args.input, ['.mp4', '.avi', '.mov'])
    
    total_files = len(image_files) + len(video_files)
    if total_files == 0:
        logging.warning(f"処理対象ファイルが見つかりません: {args.input}")
        return
    
    logging.info(f"画像{len(image_files)}個、動画{len(video_files)}個を処理します")
    
    processed_count = 0
    
    # 画像処理
    for image_file in tqdm(image_files, desc="画像処理"):
        if remove_background_from_image(image_file, args.output, session):
            processed_count += 1
    
    # 動画処理
    for video_file in video_files:
        if process_video_frames(video_file, args.output, session, args.fps):
            processed_count += 1
    
    logging.info(f"処理完了: {processed_count}/{total_files}個のファイル")

if __name__ == "__main__":
    main()

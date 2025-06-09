#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動画から一定間隔でフレームを抽出するツール
"""

import sys
import logging
import subprocess
from pathlib import Path

# 親ディレクトリのcommon.pyをインポート
sys.path.append(str(Path(__file__).parent.parent))
from common import setup_logging, create_base_parser, validate_directories, get_files_by_extension

def extract_frames_from_video(input_file: Path, output_dir: str, interval: int = 1, 
                            quality: int = 2, format: str = 'jpg') -> bool:
    """動画から一定間隔でフレームを抽出"""
    try:
        output_pattern = Path(output_dir) / f"{input_file.stem}_%05d.{format}"
        
        cmd = [
            "ffmpeg", "-i", str(input_file),
            "-vf", f"fps=1/{interval}",
            "-q:v", str(quality),
            "-y", str(output_pattern)
        ]
        
        logging.info(f"フレーム抽出開始: {input_file.name} ({interval}秒間隔)")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 出力されたファイル数をカウント
            output_files = list(Path(output_dir).glob(f"{input_file.stem}_*.{format}"))
            logging.info(f"フレーム抽出完了: {input_file.name} -> {len(output_files)}フレーム")
            return True
        else:
            logging.error(f"フレーム抽出エラー {input_file.name}: {result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"フレーム抽出エラー {input_file.name}: {e}")
        return False

def main():
    parser = create_base_parser("動画フレーム抽出ツール")
    parser.add_argument('-n', '--interval', type=int, default=1,
                       help='フレーム抽出間隔（秒） (デフォルト: 1)')
    parser.add_argument('-q', '--quality', type=int, default=2,
                       help='画質設定 1-31 (低いほど高品質、デフォルト: 2)')
    parser.add_argument('-f', '--format', choices=['jpg', 'png'], default='jpg',
                       help='出力フォーマット (デフォルト: jpg)')
    args = parser.parse_args()
    
    setup_logging()
    
    if not validate_directories(args.input, args.output):
        sys.exit(1)
    
    # 動画ファイルを取得
    video_files = get_files_by_extension(args.input, ['.mp4', '.avi', '.mov', '.mkv'])
    
    if not video_files:
        logging.warning(f"動画ファイルが見つかりません: {args.input}")
        return
    
    logging.info(f"{len(video_files)}個の動画から{args.interval}秒間隔でフレームを抽出します")
    
    processed_count = 0
    for video_file in video_files:
        if extract_frames_from_video(video_file, args.output, args.interval, 
                                   args.quality, args.format):
            processed_count += 1
    
    logging.info(f"フレーム抽出完了: {processed_count}/{len(video_files)}個の動画")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動画を一定時間ごとに分割するツール
"""

import sys
import logging
import subprocess
from pathlib import Path

# 親ディレクトリのcommon.pyをインポート
sys.path.append(str(Path(__file__).parent.parent))
from common import setup_logging, create_base_parser, validate_directories, get_files_by_extension

def divide_video_by_time(input_file: Path, output_dir: str, minutes: int = 30) -> bool:
    """動画を指定時間ごとに分割"""
    try:
        output_pattern = Path(output_dir) / f"{input_file.stem}_%04d.mp4"
        segment_time = f"{minutes}:00"
        
        cmd = [
            "ffmpeg", "-i", str(input_file),
            "-c", "copy",  # コーデックをコピー（再エンコードなし）
            "-map", "0",   # すべてのストリームを選択
            "-segment_time", segment_time,
            "-f", "segment",
            "-reset_timestamps", "1",
            "-y", str(output_pattern)
        ]
        
        logging.info(f"動画分割開始: {input_file.name} ({minutes}分間隔)")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 出力されたファイル数をカウント
            output_files = list(Path(output_dir).glob(f"{input_file.stem}_*.mp4"))
            logging.info(f"動画分割完了: {input_file.name} -> {len(output_files)}セグメント")
            return True
        else:
            logging.error(f"動画分割エラー {input_file.name}: {result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"動画分割エラー {input_file.name}: {e}")
        return False

def main():
    parser = create_base_parser("動画分割ツール")
    parser.add_argument('-m', '--minutes', type=int, default=30,
                       help='分割時間（分） (デフォルト: 30)')
    parser.add_argument('--reencode', action='store_true',
                       help='再エンコードを行う（品質向上、処理時間増加）')
    args = parser.parse_args()
    
    setup_logging()
    
    if not validate_directories(args.input, args.output):
        sys.exit(1)
    
    # 動画ファイルを取得
    video_files = get_files_by_extension(args.input, ['.mp4', '.avi', '.mov', '.mkv'])
    
    if not video_files:
        logging.warning(f"動画ファイルが見つかりません: {args.input}")
        return
    
    logging.info(f"{len(video_files)}個の動画を{args.minutes}分間隔で分割します")
    
    processed_count = 0
    for video_file in video_files:
        if divide_video_by_time(video_file, args.output, args.minutes):
            processed_count += 1
    
    logging.info(f"動画分割完了: {processed_count}/{len(video_files)}個の動画")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import argparse
import glob
from pathlib import Path

def divide_video(input_file, output_dir, minutes=10):
    """
    指定された動画ファイルを一定時間ごとに分割する
    
    Args:
        input_file (str): 入力動画ファイルのパス
        output_dir (str): 出力先ディレクトリのパス
        minutes (int): 分割する時間（分）
    """
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)
    
    # 入力ファイル名（拡張子なし）を取得
    file_name = os.path.basename(input_file)
    name_without_ext = os.path.splitext(file_name)[0]
    
    # 出力ファイルのパターン
    output_pattern = os.path.join(output_dir, f"{name_without_ext}_%04d.mp4")
    
    # 分をHH:MM:SS形式に変換
    segment_time = f"{minutes}:00"
    
    # FFmpegコマンドを実行
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-c", "copy",  # コーデックをコピー（再エンコードなし）
        "-map", "0",   # すべてのストリームを選択
        "-segment_time", segment_time,
        "-f", "segment",
        "-reset_timestamps", "1",
        output_pattern
    ]
    
    print(f"実行コマンド: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"{input_file} を {minutes}分ごとに分割しました。")
    except subprocess.CalledProcessError as e:
        print(f"エラーが発生しました: {e}")

def main():
    parser = argparse.ArgumentParser(description='動画ファイルを一定時間ごとに分割します')
    parser.add_argument('-m', '--minutes', type=int, default=30,
                        help='分割する時間（分）、デフォルトは30分')
    parser.add_argument('-i', '--input-dir', type=str, default='data/input',
                        help='入力ディレクトリ、デフォルトは data/input')
    parser.add_argument('-o', '--output-dir', type=str, default='data/output',
                        help='出力ディレクトリ、デフォルトは data/output')
    args = parser.parse_args()
    
    # 入力ディレクトリ内のすべての.mp4ファイルを取得
    input_dir = Path(args.input_dir)
    mp4_files = list(input_dir.glob('*.mp4'))
    
    if not mp4_files:
        print(f"{args.input_dir} ディレクトリに.mp4ファイルが見つかりませんでした。")
        return
    
    print(f"{len(mp4_files)}個の.mp4ファイルが見つかりました。")
    
    # 各ファイルを処理
    for mp4_file in mp4_files:
        print(f"処理中: {mp4_file}")
        divide_video(str(mp4_file), args.output_dir, args.minutes)

if __name__ == "__main__":
    main()

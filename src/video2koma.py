#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import argparse
from pathlib import Path

def extract_frames(input_file, output_dir, interval=1):
    """
    指定された動画ファイルからn秒ごとに1フレームを抽出する
    
    Args:
        input_file (str): 入力動画ファイルのパス
        output_dir (str): 出力先ディレクトリのパス
        interval (int): フレーム抽出間隔（秒）、デフォルトは1秒
    """
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)
    
    # 入力ファイル名（拡張子なし）を取得
    file_name = os.path.basename(input_file)
    name_without_ext = os.path.splitext(file_name)[0]
    
    # 出力ファイルのパターン
    output_pattern = os.path.join(output_dir, f"{name_without_ext}_%05d.jpg")
    
    # FFmpegコマンドを実行
    # -r オプションで1秒あたりのフレームレートを指定（1/intervalで指定秒数ごとに1フレーム）
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-vf", f"fps=1/{interval}",  # n秒ごとに1フレーム
        "-q:v", "2",  # 画質設定（2は高品質）
        output_pattern
    ]
    
    print(f"実行コマンド: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"{input_file} から {interval}秒ごとにフレームを抽出しました。")
    except subprocess.CalledProcessError as e:
        print(f"エラーが発生しました: {e}")

def main():
    parser = argparse.ArgumentParser(description='動画ファイルからn秒ごとに1フレームを抽出します')
    parser.add_argument('-n', '--interval', type=int, default=1,
                        help='フレーム抽出間隔（秒）、デフォルトは1秒')
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
        extract_frames(str(mp4_file), args.output_dir, args.interval)

if __name__ == "__main__":
    main()

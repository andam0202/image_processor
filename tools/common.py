#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
from pathlib import Path
from typing import List, Optional
import logging

def setup_logging(log_file: Optional[str] = None) -> None:
    """ログ設定をセットアップ"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if log_file:
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

def create_directory(path: str) -> None:
    """ディレクトリを作成（存在しない場合）"""
    os.makedirs(path, exist_ok=True)

def get_files_by_extension(directory: str, extensions: List[str]) -> List[Path]:
    """指定された拡張子のファイルを取得"""
    directory_path = Path(directory)
    files = []
    for ext in extensions:
        files.extend(directory_path.glob(f'*{ext}'))
        files.extend(directory_path.glob(f'*{ext.upper()}'))
    return sorted(files)

def create_base_parser(description: str) -> argparse.ArgumentParser:
    """基本的なコマンドライン引数パーサーを作成"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i', '--input', 
                       help='入力ディレクトリ', 
                       default='data/input')
    parser.add_argument('-o', '--output', 
                       help='出力ディレクトリ', 
                       default='data/output')
    parser.add_argument('-v', '--verbose', 
                       action='store_true',
                       help='詳細な出力を表示')
    return parser

def validate_directories(input_dir: str, output_dir: str) -> bool:
    """入力・出力ディレクトリの検証"""
    if not os.path.exists(input_dir):
        logging.error(f"入力ディレクトリが存在しません: {input_dir}")
        return False
    
    create_directory(output_dir)
    return True

def remove_file_safely(file_path: str) -> bool:
    """ファイルを安全に削除"""
    try:
        os.remove(file_path)
        return True
    except OSError as e:
        logging.error(f"ファイルの削除に失敗: {file_path} - {e}")
        return False
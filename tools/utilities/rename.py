#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ファイル名の一括変更ツール
"""

import sys
import logging
import re
from pathlib import Path

# 親ディレクトリのcommon.pyをインポート
sys.path.append(str(Path(__file__).parent.parent))
from common import setup_logging, create_base_parser, validate_directories, get_files_by_extension

def sequential_rename(input_dir: str, prefix: str = "file", start_num: int = 0, 
                     zero_fill: int = 4, extensions: list = None) -> bool:
    """ファイルを連番でリネーム"""
    try:
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.mp4']
        
        files = get_files_by_extension(input_dir, extensions)
        
        if not files:
            logging.warning("対象ファイルが見つかりません")
            return False
        
        # ファイルをソート
        files.sort()
        
        renamed_count = 0
        for i, file_path in enumerate(files):
            new_name = f"{prefix}_{str(start_num + i).zfill(zero_fill)}{file_path.suffix}"
            new_path = file_path.parent / new_name
            
            if new_path != file_path:
                file_path.rename(new_path)
                logging.info(f"リネーム: {file_path.name} -> {new_name}")
                renamed_count += 1
        
        logging.info(f"連番リネーム完了: {renamed_count}個のファイル")
        return True
        
    except Exception as e:
        logging.error(f"連番リネームエラー: {e}")
        return False

def pattern_rename(input_dir: str, pattern: str, replacement: str, extensions: list = None) -> bool:
    """正規表現パターンでリネーム"""
    try:
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.mp4']
        
        files = get_files_by_extension(input_dir, extensions)
        
        if not files:
            logging.warning("対象ファイルが見つかりません")
            return False
        
        renamed_count = 0
        for file_path in files:
            name_without_ext = file_path.stem
            new_name = re.sub(pattern, replacement, name_without_ext)
            
            if new_name != name_without_ext:
                new_path = file_path.parent / f"{new_name}{file_path.suffix}"
                
                # 同名ファイルが存在する場合はスキップ
                if new_path.exists():
                    logging.warning(f"スキップ（同名ファイル存在）: {file_path.name}")
                    continue
                
                file_path.rename(new_path)
                logging.info(f"リネーム: {file_path.name} -> {new_path.name}")
                renamed_count += 1
        
        logging.info(f"パターンリネーム完了: {renamed_count}個のファイル")
        return True
        
    except Exception as e:
        logging.error(f"パターンリネームエラー: {e}")
        return False

def zero_padding_rename(input_dir: str, padding: int = 4, extensions: list = None) -> bool:
    """ファイル名の数字部分をゼロパディング"""
    try:
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.mp4']
        
        files = get_files_by_extension(input_dir, extensions)
        
        if not files:
            logging.warning("対象ファイルが見つかりません")
            return False
        
        renamed_count = 0
        for file_path in files:
            name_without_ext = file_path.stem
            
            # 数字部分を見つけてゼロパディング
            def replace_number(match):
                return str(int(match.group())).zfill(padding)
            
            new_name = re.sub(r'\d+', replace_number, name_without_ext)
            
            if new_name != name_without_ext:
                new_path = file_path.parent / f"{new_name}{file_path.suffix}"
                
                if new_path.exists():
                    logging.warning(f"スキップ（同名ファイル存在）: {file_path.name}")
                    continue
                
                file_path.rename(new_path)
                logging.info(f"リネーム: {file_path.name} -> {new_path.name}")
                renamed_count += 1
        
        logging.info(f"ゼロパディング完了: {renamed_count}個のファイル")
        return True
        
    except Exception as e:
        logging.error(f"ゼロパディングエラー: {e}")
        return False

def main():
    parser = create_base_parser("ファイル名一括変更ツール")
    
    # サブコマンドを追加
    subparsers = parser.add_subparsers(dest='command', help='リネーム方法')
    
    # 連番リネーム
    seq_parser = subparsers.add_parser('sequential', help='連番でリネーム')
    seq_parser.add_argument('-p', '--prefix', default='file', help='プレフィックス (デフォルト: file)')
    seq_parser.add_argument('-s', '--start', type=int, default=0, help='開始番号 (デフォルト: 0)')
    seq_parser.add_argument('-z', '--zero-fill', type=int, default=4, help='ゼロパディング桁数 (デフォルト: 4)')
    
    # パターンリネーム
    pat_parser = subparsers.add_parser('pattern', help='正規表現パターンでリネーム')
    pat_parser.add_argument('-p', '--pattern', required=True, help='検索パターン（正規表現）')
    pat_parser.add_argument('-r', '--replacement', required=True, help='置換文字列')
    
    # ゼロパディング
    pad_parser = subparsers.add_parser('padding', help='数字部分をゼロパディング')
    pad_parser.add_argument('-p', '--padding', type=int, default=4, help='パディング桁数 (デフォルト: 4)')
    
    # 共通オプション
    for p in [seq_parser, pat_parser, pad_parser]:
        p.add_argument('--extensions', nargs='+', 
                      default=['.jpg', '.jpeg', '.png', '.mp4'],
                      help='対象拡張子')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    setup_logging()
    
    if not validate_directories(args.input, None):
        sys.exit(1)
    
    success = False
    
    if args.command == 'sequential':
        success = sequential_rename(args.input, args.prefix, args.start, 
                                  args.zero_fill, args.extensions)
    elif args.command == 'pattern':
        success = pattern_rename(args.input, args.pattern, args.replacement, 
                               args.extensions)
    elif args.command == 'padding':
        success = zero_padding_rename(args.input, args.padding, args.extensions)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()

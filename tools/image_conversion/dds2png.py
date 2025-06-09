#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DDSファイルをPNGファイルに変換するツール
依存関係: pip install Wand, ImageMagickのインストールも必要
"""

import sys
import logging
from pathlib import Path

try:
    from wand.image import Image as WandImage
except ImportError:
    print("Error: wandライブラリがインストールされていません。")
    print("以下のコマンドでインストールしてください:")
    print("pip install Wand")
    print("また、ImageMagickもシステムにインストールする必要があります。")
    sys.exit(1)

# 親ディレクトリのcommon.pyをインポート
sys.path.append(str(Path(__file__).parent.parent))
from common import setup_logging, create_base_parser, validate_directories, get_files_by_extension, remove_file_safely

def convert_dds_to_png(input_file: Path, output_dir: str) -> bool:
    """DDSファイルをPNGに変換"""
    try:
        with WandImage(filename=str(input_file)) as img:
            png_filename = input_file.stem + '.png'
            output_path = Path(output_dir) / png_filename
            
            img.save(filename=str(output_path))
            logging.info(f"変換完了: {input_file.name} -> {png_filename}")
            return True
            
    except Exception as e:
        logging.error(f"変換エラー {input_file.name}: {e}")
        return False

def main():
    parser = create_base_parser("DDSファイルをPNGファイルに変換")
    parser.add_argument('--keep-original', action='store_true',
                       help='変換後も元のDDSファイルを保持')
    args = parser.parse_args()
    
    setup_logging()
    
    if not validate_directories(args.input, args.output):
        sys.exit(1)
    
    dds_files = get_files_by_extension(args.input, ['.dds'])
    
    if not dds_files:
        logging.warning(f"DDSファイルが見つかりません: {args.input}")
        return
    
    logging.info(f"{len(dds_files)}個のDDSファイルを処理します")
    
    converted_count = 0
    for dds_file in dds_files:
        if convert_dds_to_png(dds_file, args.output):
            converted_count += 1
            if not args.keep_original:
                remove_file_safely(str(dds_file))
    
    logging.info(f"変換完了: {converted_count}/{len(dds_files)}個のファイル")

if __name__ == "__main__":
    main()

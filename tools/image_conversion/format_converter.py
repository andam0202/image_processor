#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像フォーマット変換ツール（JPG, WebP, PNG間の変換）
"""

import sys
import logging
from pathlib import Path
from PIL import Image

# 親ディレクトリのcommon.pyをインポート
sys.path.append(str(Path(__file__).parent.parent))
from common import setup_logging, create_base_parser, validate_directories, get_files_by_extension, remove_file_safely

def convert_image(input_file: Path, output_dir: str, target_format: str, keep_original: bool = False) -> bool:
    """画像を指定フォーマットに変換"""
    try:
        with Image.open(input_file) as img:
            # RGBAモードの場合、JPGに変換する時はRGBに変換
            if target_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # 拡張子を決定
            ext_map = {'JPEG': '.jpg', 'PNG': '.png', 'WEBP': '.webp'}
            new_ext = ext_map.get(target_format.upper(), '.png')
            
            output_filename = input_file.stem + new_ext
            output_path = Path(output_dir) / output_filename
            
            # 保存
            img.save(output_path, target_format.upper())
            logging.info(f"変換完了: {input_file.name} -> {output_filename}")
            
            # 元ファイルの削除（形式が変わる場合のみ）
            if not keep_original and input_file.suffix.lower() != new_ext.lower():
                remove_file_safely(str(input_file))
            
            return True
            
    except Exception as e:
        logging.error(f"変換エラー {input_file.name}: {e}")
        return False

def main():
    parser = create_base_parser("画像フォーマット変換ツール")
    parser.add_argument('-f', '--format', 
                       choices=['png', 'jpg', 'jpeg', 'webp'],
                       default='png',
                       help='変換先フォーマット (デフォルト: png)')
    parser.add_argument('--keep-original', action='store_true',
                       help='変換後も元ファイルを保持')
    parser.add_argument('--extensions', nargs='+',
                       default=['.jpg', '.jpeg', '.png', '.webp'],
                       help='処理対象の拡張子')
    args = parser.parse_args()
    
    setup_logging()
    
    if not validate_directories(args.input, args.output):
        sys.exit(1)
    
    # JPEGとJPGを統一
    target_format = 'JPEG' if args.format.lower() in ['jpg', 'jpeg'] else args.format.upper()
    
    image_files = get_files_by_extension(args.input, args.extensions)
    
    if not image_files:
        logging.warning(f"対象ファイルが見つかりません: {args.input}")
        return
    
    logging.info(f"{len(image_files)}個のファイルを{target_format}形式に変換します")
    
    converted_count = 0
    for image_file in image_files:
        if convert_image(image_file, args.output, target_format, args.keep_original):
            converted_count += 1
    
    logging.info(f"変換完了: {converted_count}/{len(image_files)}個のファイル")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4コマ漫画画像をコマごとに分割するツール
デフォルトは学マス仕様だが、座標をカスタマイズ可能
"""

import sys
import logging
from pathlib import Path
from PIL import Image
from typing import List, Tuple

# 親ディレクトリのcommon.pyをインポート
sys.path.append(str(Path(__file__).parent.parent))
from common import setup_logging, create_base_parser, validate_directories, get_files_by_extension

# 学マス4コマのデフォルト座標 (x1, y1, x2, y2)
DEFAULT_COORDINATES = [
    (104, 231, 799, 751),   # 1コマ目
    (104, 795, 799, 1315),  # 2コマ目  
    (104, 1359, 799, 1879), # 3コマ目
    (104, 1923, 799, 2443)  # 4コマ目
]

def split_koma_image(input_file: Path, output_dir: str, coordinates: List[Tuple[int, int, int, int]]) -> bool:
    """4コマ漫画を各コマに分割"""
    try:
        with Image.open(input_file) as img:
            base_name = input_file.stem
            
            for i, (x1, y1, x2, y2) in enumerate(coordinates, 1):
                cropped = img.crop((x1, y1, x2, y2))
                output_path = Path(output_dir) / f"{base_name}_koma{i}.jpg"
                cropped.save(output_path, 'JPEG', quality=95)
                
            logging.info(f"分割完了: {input_file.name} -> {len(coordinates)}コマ")
            return True
            
    except Exception as e:
        logging.error(f"分割エラー {input_file.name}: {e}")
        return False

def parse_coordinates(coord_str: str) -> List[Tuple[int, int, int, int]]:
    """座標文字列をパース"""
    try:
        coords = []
        for coord_set in coord_str.split(';'):
            x1, y1, x2, y2 = map(int, coord_set.split(','))
            coords.append((x1, y1, x2, y2))
        return coords
    except ValueError as e:
        raise ValueError(f"座標フォーマットエラー: {e}")

def main():
    parser = create_base_parser("4コマ漫画画像の分割ツール")
    parser.add_argument('--coordinates', type=str,
                       help='カスタム座標 (例: "104,231,799,751;104,795,799,1315;...")')
    parser.add_argument('--format', choices=['jpg', 'png'], default='jpg',
                       help='出力フォーマット (デフォルト: jpg)')
    parser.add_argument('--quality', type=int, default=95,
                       help='JPEG品質 1-100 (デフォルト: 95)')
    args = parser.parse_args()
    
    setup_logging()
    
    if not validate_directories(args.input, args.output):
        sys.exit(1)
    
    # 座標の設定
    if args.coordinates:
        try:
            coordinates = parse_coordinates(args.coordinates)
            logging.info(f"カスタム座標を使用: {len(coordinates)}コマ")
        except ValueError as e:
            logging.error(f"座標エラー: {e}")
            sys.exit(1)
    else:
        coordinates = DEFAULT_COORDINATES
        logging.info("学マスデフォルト座標を使用")
    
    # 画像ファイルを取得
    image_files = get_files_by_extension(args.input, ['.jpg', '.jpeg', '.png'])
    
    if not image_files:
        logging.warning(f"画像ファイルが見つかりません: {args.input}")
        return
    
    logging.info(f"{len(image_files)}個の画像を{len(coordinates)}コマに分割します")
    
    processed_count = 0
    for image_file in image_files:
        if split_koma_image(image_file, args.output, coordinates):
            processed_count += 1
    
    logging.info(f"分割完了: {processed_count}/{len(image_files)}個の画像")

if __name__ == "__main__":
    main()

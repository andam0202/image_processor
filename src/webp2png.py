# data/inputフォルダ内のwebpファイルをpngファイルに変換してdata/inputフォルダに保存する

import os
from PIL import Image

# 入力フォルダと出力フォルダのパスを指定
input_folder = 'data/input'
output_folder = 'data/input'

# 出力フォルダが存在しない場合は作成する
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 入力フォルダ内のすべてのファイルを確認
for filename in os.listdir(input_folder):
    # ファイルがWEBP形式かどうかをチェック
    if filename.endswith('.webp'):
        # WEBPファイルのフルパスを取得
        webp_path = os.path.join(input_folder, filename)
        
        # 画像を開く
        with Image.open(webp_path) as img:
            # PNG形式で保存するためのファイル名を設定
            png_filename = filename.rsplit('.', 1)[0] + '.png'
            png_path = os.path.join(output_folder, png_filename)
            
            # 画像をPNG形式で保存
            img.save(png_path, 'PNG')
            
            # 元のWEBPファイルを削除
            os.remove(webp_path)

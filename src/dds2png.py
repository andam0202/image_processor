# data/inputフォルダ内のDDSファイルをPNGファイルに変換してdata/inputフォルダに保存する
# pip install Wand
# sudo apt upgrade
# sudo apt install imagemagick

import os
import sys
from PIL import Image

try:
    from wand.image import Image as WandImage
except ImportError:
    print("wandライブラリがインストールされていません。")
    print("pip install Wand を実行してインストールしてください。")
    print("また、ImageMagickもインストールする必要があります。")
    sys.exit(1)

def dds2png():
    # 入力フォルダと出力フォルダのパスを指定
    input_folder = 'data/input'
    output_folder = 'data/output'

    # 出力フォルダが存在しない場合は作成する
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 変換されたファイル数をカウント
    converted_count = 0

    # 入力フォルダ内のすべてのファイルを確認
    for filename in os.listdir(input_folder):
        # ファイルがDDS形式かどうかをチェック（大文字小文字を区別しない）
        if filename.lower().endswith('.dds'):
            # DDSファイルのフルパスを取得
            dds_path = os.path.join(input_folder, filename)
            
            try:
                # wandライブラリを使用してDDSファイルを開く
                with WandImage(filename=dds_path) as img:
                    # PNG形式で保存するためのファイル名を設定
                    png_filename = filename.rsplit('.', 1)[0] + '.png'
                    png_path = os.path.join(output_folder, png_filename)
                    
                    # 画像をPNG形式で保存
                    img.save(filename=png_path)
                    
                    # 元のDDSファイルを削除
                    os.remove(dds_path)
                    
                    converted_count += 1
                    print(f"変換完了: {filename} -> {png_filename}")
            
            except Exception as e:
                print(f"エラー: {filename}の変換中に問題が発生しました - {str(e)}")
    
    if converted_count > 0:
        print(f"合計{converted_count}個のDDSファイルをPNGに変換しました。")
    else:
        print("変換可能なDDSファイルが見つかりませんでした。")

if __name__ == "__main__":
    dds2png()

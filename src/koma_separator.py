# 学マスの4コマ漫画画像をコマごとに分割するプログラム

# python3 koma_separator.py -i ../data/input -o ../data/output

# diff x695  y564
# 1コマ目は(104, 231) -> (799, 751)
# 2コマ目は(104, 795) -> (799, 1315)
# 3コマ目は(104, 1359) -> (799, 1879)
# 4コマ目は(104, 1923) -> (799, 2443)


import os
import argparse
from PIL import Image
import icecream as ic


def main():
    parser = argparse.ArgumentParser(description='学マスの4コマ漫画画像をコマごとに分割するプログラム')
    parser.add_argument('-i', '--input', help='入力画像のディレクトリ', required=False, default='data/input')
    parser.add_argument('-o', '--output', help='出力画像のディレクトリ', required=False, default='data/output')
    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(input_dir):
        ic.ic(file)
        if file.endswith('.jpg'):
            img_path = os.path.join(input_dir, file)
            img = Image.open(img_path)
            
            img1 = img.crop((104, 231, 799, 751))
            img2 = img.crop((104, 795, 799, 1315))
            img3 = img.crop((104, 1359, 799, 1879))
            img4 = img.crop((104, 1923, 799, 2443))

            base_filename = os.path.splitext(file)[0]
            ic.ic(base_filename)
            
            img1.save(os.path.join(output_dir, f"{base_filename}_1.jpg"))
            img2.save(os.path.join(output_dir, f"{base_filename}_2.jpg"))
            img3.save(os.path.join(output_dir, f"{base_filename}_3.jpg"))
            img4.save(os.path.join(output_dir, f"{base_filename}_4.jpg"))


if __name__=="__main__":
    main()

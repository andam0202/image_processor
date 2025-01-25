import os
import argparse

def rename(): # ファイル名を変更する関数
    # 元々のファイル名はimg_comics_0-scaled.jpgとなっているので、
    # まずは数字の部分について0埋めを行う
    # 例: img_comics_0-scaled.jpg -> img_comics_0000-scaled.jpg
    for file in os.listdir('data/input'):
        if file.endswith('.jpg'):
            num = file.split('_')[2].split('-')[0]
            os.rename(os.path.join('data/input', file), os.path.join('data/input', 'img_comics_' + str(num).zfill(4) + '-scaled.jpg'))

    
    # xxx.jpgを上から順番にgakumasu4koma_0000.jpgに変更
    i = 0
    for file in os.listdir('data/input'):
        if file.endswith('.jpg'):
            os.rename(os.path.join('data/input', file), os.path.join('data/input', 'gakumasu4koma_' + str(i).zfill(4) + '.jpg'))
            i += 1
            
def main():
    rename()


if __name__=="__main__":
    main()

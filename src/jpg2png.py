import os
from PIL import Image

def jpg2png():
    for file in os.listdir('data/input'):
        if file.endswith('.jpg'):
            img_path = os.path.join('data/input', file)
            img = Image.open(img_path)
            img_path = os.path.join('data/input', file.replace(".jpg", ".png"))
            img.save(img_path)
            
            # 元のjpgファイルを削除
            os.remove(os.path.join('data/input', file))

if __name__=="__main__":
    jpg2png()
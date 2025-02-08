# 指定されたフォルダ内の画像を透過処理する
import os
import argparse
from rembg import remove, new_session
from PIL import Image
from tqdm import tqdm
import icecream as ic

def process_images():
    import logging
    logging.basicConfig(filename='process_images.log', level=logging.ERROR)
    parser = argparse.ArgumentParser(description='指定されたフォルダ内の画像を透過処理する')
    parser.add_argument('-i', '--input', help='入力画像のディレクトリ', required=False, default='data/input')
    parser.add_argument('-o', '--output', help='出力画像のディレクトリ', required=False, default='data/output')
    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # outputフォルダ内を空にする
    for file in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, file))
    
    # isnet-anime
    model_list = ["isnet-general-use", "isnet-anime", "birefnet-general", "birefnet-general-lite"]
    session = new_session("isnet-anime")

    try:
        for file in os.listdir(input_dir):
            if file.endswith('.jpg') or file.endswith('.png'):
                img_path = os.path.join(input_dir, file)
                img = Image.open(img_path)
                ic.ic(img_path)
                ic.ic(img)
                img = Image.open(img_path)
                img = remove(img, session=session)
                img.save(os.path.join(output_dir, file))
                
            elif file.endswith('.mp4'):
                # まずは動画をフレームごとに分割
                os.system(f"ffmpeg -i {os.path.join(input_dir, file)} -vf fps=30 {os.path.join(output_dir, file.replace('.mp4', ''))}_%04d.png")
                
                # また、動画をフレームごとに分割してinputフォルダに保存する
                for i, image in enumerate(os.listdir(output_dir)):
                    img_path = os.path.join(output_dir, image)
                    img = Image.open(img_path)
                    img.save(os.path.join(input_dir, f"{file.replace('.mp4', '')}_{i:04d}.png"))
                
                
                # 画像を透過処理
                for image in tqdm(os.listdir(output_dir)):
                    img_path = os.path.join(output_dir, image)
                    img = Image.open(img_path).convert("RGBA")
                    img = remove(img, post_process_mask=True, session=session)
                    img.save(os.path.join(output_dir, image))
                    
                    # cliで実行する場合
                    # command = f"rembg i {os.path.join(output_dir, image)} -m birefnet-general-lite {os.path.join(output_dir, image)}"
                    # os.system(command)
                    
                # 最後に動画に戻す
                command = f"ffmpeg -r 3 -i {os.path.join(output_dir, file.replace('.mp4', ''))}_%04d.png -vcodec libx264 -pix_fmt yuv420p {os.path.join(output_dir, file.replace('.mp4', '_output.mp4'))}"
                os.system(command)
                
            else:
                print(f"Unsupported file type: {file}")
                logging.error(f"Unsupported file type: {file}")
                
    except Exception as e:
        print(f"Error processing file {file}: {e}")
        logging.error(f"Error processing file {file}: {e}")


if __name__=="__main__":
    process_images()
